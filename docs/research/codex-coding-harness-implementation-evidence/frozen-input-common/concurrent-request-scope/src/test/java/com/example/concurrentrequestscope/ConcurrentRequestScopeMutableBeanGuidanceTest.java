package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.support.ManagedExecutorExampleConfig;
import com.example.concurrentrequestscope.support.MutableBeanGuidanceConfig;
import io.micrometer.context.ContextRegistry;
import io.micrometer.context.integration.Slf4jThreadLocalAccessor;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.HashSet;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executor;
import java.util.concurrent.TimeUnit;
import java.util.function.IntFunction;
import java.util.stream.IntStream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

@SpringJUnitConfig({ManagedExecutorExampleConfig.class, MutableBeanGuidanceConfig.class})
@TestPropertySource(properties = "concurrent-request-scope.testing.clear-enabled=true")
class ConcurrentRequestScopeMutableBeanGuidanceTest {

    @Autowired
    private MutableBeanGuidanceConfig.AtomicCounterScopedBean atomicCounter;

    @Autowired
    private MutableBeanGuidanceConfig.ConcurrentQueueScopedBean concurrentQueue;

    @Autowired
    private MutableBeanGuidanceConfig.LockedAccumulatorScopedBean lockedAccumulator;

    @Autowired
    private MutableBeanGuidanceConfig.DeferredWriteScopedBean deferredWrite;

    @Autowired
    private MutableBeanGuidanceConfig.UnsafeOverlapScopedBean unsafeOverlap;

    @Autowired
    @Qualifier("virtualRequestAwareExecutor")
    private Executor virtualRequestAwareExecutor;

    @Autowired
    private ConfigurableListableBeanFactory beanFactory;

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        MDC.clear();
        registeredScope().clearForTesting();
    }

    @AfterAll
    static void removeMdcAccessor() {
        ContextRegistry.getInstance().removeThreadLocalAccessor(Slf4jThreadLocalAccessor.KEY);
    }

    @Test
    void atomicCounterSharesSameScopedBeanAndCountsAllWorkers() throws Exception {
        bindRequest();
        int workers = 16;
        String mainThreadBeanId = atomicCounter.id();

        List<String> workerBeanIds = runWorkers(workers, ignored -> {
            atomicCounter.increment();
            return atomicCounter.id();
        });

        assertEquals(workers, atomicCounter.count());
        assertEquals(List.of(mainThreadBeanId), new HashSet<>(workerBeanIds).stream().toList());
    }

    @Test
    void concurrentQueueSharesSameScopedBeanAndReceivesAllValues() throws Exception {
        bindRequest();
        int workers = 12;
        String mainThreadBeanId = concurrentQueue.id();

        List<String> workerBeanIds = runWorkers(workers, index -> {
            concurrentQueue.add(index);
            return concurrentQueue.id();
        });

        assertEquals(List.of(mainThreadBeanId), new HashSet<>(workerBeanIds).stream().toList());
        assertEquals(workers, concurrentQueue.snapshot().size());
        assertEquals(IntStream.range(0, workers).boxed().toList(),
                concurrentQueue.snapshot().stream().sorted().toList());
    }

    @Test
    void lockedAccumulatorSharesSameScopedBeanAndComputesDeterministicSum() throws Exception {
        bindRequest();
        int workers = 10;
        String mainThreadBeanId = lockedAccumulator.id();

        List<String> workerBeanIds = runWorkers(workers, index -> {
            lockedAccumulator.add(index + 1);
            return lockedAccumulator.id();
        });

        assertEquals(List.of(mainThreadBeanId), new HashSet<>(workerBeanIds).stream().toList());
        assertEquals(55, lockedAccumulator.sum());
    }

    @Test
    void deferredWriteKeepsScopedBeanMutationOnRequestThreadAfterWorkersJoin() throws Exception {
        bindRequest();
        int workers = 8;

        List<Integer> workerResults = runWorkers(workers, index -> index * 2);
        deferredWrite.recordAfterWorkersJoin(workerResults);

        assertEquals(IntStream.range(0, workers).map(index -> index * 2).boxed().toList(),
                deferredWrite.values().stream().sorted().toList());
    }

    @Test
    void concurrentRequestScopeDoesNotSerializeScopedBeanMethodCalls() throws Exception {
        bindRequest();
        int workers = 4;
        String mainThreadBeanId = unsafeOverlap.id();
        CountDownLatch entered = new CountDownLatch(workers);
        CountDownLatch release = new CountDownLatch(1);
        List<CompletableFuture<String>> futures = IntStream.range(0, workers)
                .mapToObj(index -> CompletableFuture.supplyAsync(() -> {
                    unsafeOverlap.enterUnsynchronizedMethod(entered, release);
                    return unsafeOverlap.id();
                }, virtualRequestAwareExecutor))
                .toList();

        try {
            assertTrue(entered.await(5, TimeUnit.SECONDS));
            assertTrue(unsafeOverlap.maxConcurrentCalls() > 1,
                    "ConcurrentRequestScope shares bean identity but does not serialize bean method calls");
        } finally {
            release.countDown();
        }

        CompletableFuture.allOf(futures.toArray(CompletableFuture[]::new))
                .get(5, TimeUnit.SECONDS);
        List<String> workerBeanIds = futures.stream()
                .map(CompletableFuture::join)
                .toList();
        assertEquals(List.of(mainThreadBeanId), new HashSet<>(workerBeanIds).stream().toList());
    }

    private <T> List<T> runWorkers(int workers, IntFunction<T> task) throws Exception {
        List<CompletableFuture<T>> futures = IntStream.range(0, workers)
                .mapToObj(index -> CompletableFuture.supplyAsync(
                        () -> task.apply(index),
                        virtualRequestAwareExecutor))
                .toList();
        CompletableFuture.allOf(futures.toArray(CompletableFuture[]::new))
                .get(5, TimeUnit.SECONDS);
        return futures.stream()
                .map(CompletableFuture::join)
                .toList();
    }

    private static ServletRequestAttributes bindRequest() {
        ServletRequestAttributes attrs = new ServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);
        return attrs;
    }

    private ConcurrentRequestScope registeredScope() {
        return (ConcurrentRequestScope) beanFactory.getRegisteredScope(
                ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE);
    }
}
