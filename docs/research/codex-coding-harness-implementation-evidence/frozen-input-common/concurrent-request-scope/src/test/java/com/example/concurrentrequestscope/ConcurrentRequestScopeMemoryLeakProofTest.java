package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.lang.ref.WeakReference;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

import static com.example.concurrentrequestscope.support.ConcurrentRequestScopeStateAssertions.assertBaseline;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ConcurrentRequestScopeMemoryLeakProofTest {

    private static final Duration GC_TIMEOUT = Duration.ofSeconds(5);

    private ConcurrentRequestScope scope;

    @BeforeEach
    void setUp() {
        scope = new ConcurrentRequestScope(new ConcurrentRequestScopeSettings(200, true));
    }

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        scope.clearForTesting();
    }

    @Test
    void requestCompletionAndWorkerJoinReleaseRequestBeanAndCallbackPayloadReferences() throws Exception {
        RetainedObjects retainedObjects = createRequestWithWorkerAndCleanup();

        assertEventuallyCleared(retainedObjects.request(), "request");
        assertEventuallyCleared(retainedObjects.bean(), "scoped bean");
        assertEventuallyCleared(retainedObjects.callbackPayload(), "callback payload");
        assertBaseline(scope.stateForTesting());
    }

    @Test
    void thousandRequestCreateCompleteCyclesReturnToBaseline() {
        for (int i = 0; i < 1_000; i++) {
            RecordingServletRequestAttributes attrs =
                    new RecordingServletRequestAttributes(new MockHttpServletRequest());
            RequestContextHolder.setRequestAttributes(attrs);
            scope.get("bean-" + i, Object::new);
            attrs.runCompletionCallback();
            RequestContextHolder.resetRequestAttributes();

            if (i % 100 == 0) {
                assertBaseline(scope.stateForTesting());
            }
        }

        assertEquals(0, scope.stateForTesting().activeEntryCount());
        assertEquals(scope.stateForTesting().settings().maxActiveRequests(), scope.stateForTesting().availableCapacity());
        assertTrue(scope.stateForTesting().capacityInvariantHolds());
    }

    @Test
    void concurrentRequestChurnReturnsEntriesAndCapacityToBaseline() throws Exception {
        int workers = 64;
        CountDownLatch ready = new CountDownLatch(workers);
        CountDownLatch start = new CountDownLatch(1);
        CountDownLatch done = new CountDownLatch(workers);
        AtomicInteger callbackRuns = new AtomicInteger();
        AtomicReference<Throwable> failure = new AtomicReference<>();

        for (int i = 0; i < workers; i++) {
            int index = i;
            Thread.ofVirtual().start(() -> {
                try {
                    RecordingServletRequestAttributes attrs =
                            new RecordingServletRequestAttributes(new MockHttpServletRequest());
                    RequestContextHolder.setRequestAttributes(attrs);
                    ready.countDown();
                    assertTrue(start.await(5, TimeUnit.SECONDS));
                    scope.get("bean", Object::new);
                    scope.registerDestructionCallback("bean", callbackRuns::incrementAndGet);
                    attrs.runCompletionCallback();
                    RequestContextHolder.resetRequestAttributes();
                } catch (Throwable t) {
                    failure.compareAndSet(null, new AssertionError("worker " + index + " failed", t));
                } finally {
                    done.countDown();
                }
            });
        }

        assertTrue(ready.await(5, TimeUnit.SECONDS));
        start.countDown();
        assertTrue(done.await(10, TimeUnit.SECONDS));
        assertNull(failure.get());
        assertEquals(workers, callbackRuns.get());
        assertEquals(0, scope.stateForTesting().activeEntryCount());
        assertEquals(scope.stateForTesting().settings().maxActiveRequests(), scope.stateForTesting().availableCapacity());
        assertTrue(scope.stateForTesting().capacityInvariantHolds());
    }

    private RetainedObjects createRequestWithWorkerAndCleanup() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest();
        RecordingServletRequestAttributes attrs = new RecordingServletRequestAttributes(request);
        RequestContextHolder.setRequestAttributes(attrs);

        RetainedBean bean = new RetainedBean();
        CallbackPayload callbackPayload = new CallbackPayload();
        scope.get("bean", () -> bean);
        scope.registerDestructionCallback("bean", callbackPayload::markDestroyed);

        CountDownLatch workerDone = new CountDownLatch(1);
        AtomicReference<Throwable> workerFailure = new AtomicReference<>();
        Thread.ofVirtual().start(() -> {
            RequestContextHolder.setRequestAttributes(attrs);
            try {
                scope.get("bean", Object::new);
            } catch (Throwable t) {
                workerFailure.set(t);
            } finally {
                RequestContextHolder.resetRequestAttributes();
                workerDone.countDown();
            }
        });

        assertTrue(workerDone.await(5, TimeUnit.SECONDS));
        assertNull(workerFailure.get());
        attrs.runCompletionCallback();
        RequestContextHolder.resetRequestAttributes();

        return new RetainedObjects(
                new WeakReference<>(request),
                new WeakReference<>(bean),
                new WeakReference<>(callbackPayload));
    }

    private static void assertEventuallyCleared(WeakReference<?> reference, String label) throws Exception {
        long deadline = System.nanoTime() + GC_TIMEOUT.toNanos();
        List<byte[]> pressure = new ArrayList<>();
        while (System.nanoTime() < deadline && reference.get() != null) {
            System.gc();
            pressure.add(new byte[256 * 1024]);
            if (pressure.size() > 16) {
                pressure.clear();
            }
            Thread.sleep(25);
        }
        assertNull(reference.get(), label + " should not be retained after request cleanup");
    }

    private record RetainedObjects(
            WeakReference<MockHttpServletRequest> request,
            WeakReference<RetainedBean> bean,
            WeakReference<CallbackPayload> callbackPayload) {
    }

    private static final class RetainedBean {
    }

    private static final class CallbackPayload {
        private boolean destroyed;

        void markDestroyed() {
            destroyed = true;
        }
    }

    private static final class RecordingServletRequestAttributes extends ServletRequestAttributes {

        private Runnable callback;

        private RecordingServletRequestAttributes(MockHttpServletRequest request) {
            super(request);
        }

        @Override
        public void registerDestructionCallback(String name, Runnable callback, int scope) {
            this.callback = callback;
            super.registerDestructionCallback(name, callback, scope);
        }

        void runCompletionCallback() {
            callback.run();
        }
    }
}
