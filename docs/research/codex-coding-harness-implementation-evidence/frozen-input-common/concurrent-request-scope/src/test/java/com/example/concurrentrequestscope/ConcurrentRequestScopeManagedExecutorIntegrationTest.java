package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.support.ManagedExecutorExampleConfig;
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

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;
import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.assertThat;

@SpringJUnitConfig(ManagedExecutorExampleConfig.class)
@TestPropertySource(properties = "concurrent-request-scope.testing.clear-enabled=true")
class ConcurrentRequestScopeManagedExecutorIntegrationTest {

    @Autowired
    private ManagedExecutorExampleConfig.ManagedExecutorScopedProbe scopedProbe;

    @Autowired
    @Qualifier("requestAwareExecutor")
    private Executor requestAwareExecutor;

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
    void platformExecutorPropagatesRequestContextAndSelectedMdc() throws Exception {
        ServletRequestAttributes requestAttributes = bindRequest();
        MDC.put("app.requestId", "req-25-platform");
        MDC.put("app.method", "GET");
        MDC.put("app.path", "/phase-25/platform");
        MDC.put("app.unselected", "secret");

        String mainId = scopedProbe.id();

        WorkerResult workerResult = CompletableFuture.supplyAsync(() -> new WorkerResult(
                        scopedProbe.id(),
                        MDC.get("app.requestId"),
                        MDC.get("app.method"),
                        MDC.get("app.path"),
                        MDC.get("app.unselected"),
                        Thread.currentThread().isVirtual()), requestAwareExecutor)
                .get(5, TimeUnit.SECONDS);

        assertThat(workerResult.scopedProbeId()).isEqualTo(mainId);
        assertThat(workerResult.requestId()).isEqualTo("req-25-platform");
        assertThat(workerResult.method()).isEqualTo("GET");
        assertThat(workerResult.path()).isEqualTo("/phase-25/platform");
        assertThat(workerResult.unselected()).isNull();

        requestAttributes.requestCompleted();
    }

    @Test
    void virtualExecutorPropagatesRequestContextAndSelectedMdc() throws Exception {
        ServletRequestAttributes requestAttributes = bindRequest();
        MDC.put("app.requestId", "req-25-virtual");
        MDC.put("app.method", "POST");
        MDC.put("app.path", "/phase-25/virtual");

        String mainId = scopedProbe.id();

        WorkerResult workerResult = CompletableFuture.supplyAsync(() -> new WorkerResult(
                        scopedProbe.id(),
                        MDC.get("app.requestId"),
                        MDC.get("app.method"),
                        MDC.get("app.path"),
                        MDC.get("app.unselected"),
                        Thread.currentThread().isVirtual()), virtualRequestAwareExecutor)
                .get(5, TimeUnit.SECONDS);

        assertThat(workerResult.virtualThread()).isTrue();
        assertThat(workerResult.scopedProbeId()).isEqualTo(mainId);
        assertThat(workerResult.requestId()).isEqualTo("req-25-virtual");
        assertThat(workerResult.method()).isEqualTo("POST");
        assertThat(workerResult.path()).isEqualTo("/phase-25/virtual");

        requestAttributes.requestCompleted();
    }

    private static ServletRequestAttributes bindRequest() {
        ServletRequestAttributes requestAttributes = new ServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(requestAttributes);
        return requestAttributes;
    }

    private ConcurrentRequestScope registeredScope() {
        return (ConcurrentRequestScope) beanFactory.getRegisteredScope(
                ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE);
    }

    private record WorkerResult(
            String scopedProbeId,
            String requestId,
            String method,
            String path,
            String unselected,
            boolean virtualThread) {
    }
}
