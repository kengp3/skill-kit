package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCapacityException;
import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCleanupException;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeEntry;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeState;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static com.example.concurrentrequestscope.support.ConcurrentRequestScopeStateAssertions.assertBaseline;
import static com.example.concurrentrequestscope.support.ConcurrentRequestScopeStateAssertions.assertScopeState;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ConcurrentRequestScopeCapacityTest {

    private ConcurrentRequestScope scope;

    @BeforeEach
    void setUp() {
        scope = new ConcurrentRequestScope(new ConcurrentRequestScopeSettings(1, true));
    }

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        scope.clearForTesting();
    }

    @Test
    void capacityExceededThrowsAndDoesNotInsertFailedEntry() {
        RecordingServletRequestAttributes first =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());
        RecordingServletRequestAttributes second =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());

        RequestContextHolder.setRequestAttributes(first);
        scope.get("first", Object::new);

        RequestContextHolder.setRequestAttributes(second);
        assertThrows(ConcurrentRequestScopeCapacityException.class, () -> scope.get("second", Object::new));

        assertScopeState(scope.stateForTesting(), 1, 0);
        assertEquals(0, second.callbackRegistrations);

        first.runCompletionCallback();
        assertBaseline(scope.stateForTesting());
    }

    @Test
    void callbackRegistrationFailureRollsBackEntryAndPermit() {
        FailingRegistrationServletRequestAttributes attrs =
                new FailingRegistrationServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);

        assertThrows(ConcurrentRequestScopeCleanupException.class, () -> scope.get("bean", Object::new));

        assertBaseline(scope.stateForTesting());
    }

    @Test
    void duplicateCleanupDoesNotOverReleaseCapacity() {
        RecordingServletRequestAttributes attrs =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);

        scope.get("bean", Object::new);
        attrs.runCompletionCallback();
        attrs.runCompletionCallback();

        assertBaseline(scope.stateForTesting());
    }

    @Test
    void staleCleanupCannotRemoveNewerEntryForSameKey() {
        ConcurrentRequestScopeState state = scope.stateForTesting();
        Object key = new Object();
        ConcurrentRequestScopeEntry stale = new ConcurrentRequestScopeEntry(10);
        ConcurrentRequestScopeEntry current = new ConcurrentRequestScopeEntry(11);

        assertTrue(state.tryAcquireCapacity());
        assertNull(state.putEntryIfAbsent(key, current));
        int permitsBefore = state.availableCapacity();

        scope.cleanupScopeEntryForTesting(key, stale);

        assertSame(current, state.getEntry(key));
        assertScopeState(state, 1, permitsBefore);

        scope.cleanupScopeEntryForTesting(key, current);
        assertBaseline(state);
    }

    @Test
    void crossRequestCleanupCannotRemoveAnotherRequestEntry() {
        scope = new ConcurrentRequestScope(new ConcurrentRequestScopeSettings(2, true));
        ConcurrentRequestScopeState state = scope.stateForTesting();
        Object keyA = new Object();
        Object keyB = new Object();
        ConcurrentRequestScopeEntry entryA = new ConcurrentRequestScopeEntry(20);
        ConcurrentRequestScopeEntry entryB = new ConcurrentRequestScopeEntry(21);

        assertTrue(state.tryAcquireCapacity());
        assertTrue(state.tryAcquireCapacity());
        assertNull(state.putEntryIfAbsent(keyA, entryA));
        assertNull(state.putEntryIfAbsent(keyB, entryB));
        assertScopeState(state, 2, 0);

        scope.cleanupScopeEntryForTesting(keyA, entryB);

        assertSame(entryA, state.getEntry(keyA));
        assertSame(entryB, state.getEntry(keyB));
        assertScopeState(state, 2, 0);

        scope.cleanupScopeEntryForTesting(keyA, entryA);
        assertNull(state.getEntry(keyA));
        assertSame(entryB, state.getEntry(keyB));
        assertScopeState(state, 1, 1);

        scope.cleanupScopeEntryForTesting(keyB, entryB);
        assertBaseline(state);
    }

    @Test
    void sameRequestConcurrentEntryRaceConsumesOnePermitAndRegistersOneCallback() throws Exception {
        int workers = 30;
        scope = new ConcurrentRequestScope(new ConcurrentRequestScopeSettings(workers, true));
        RecordingServletRequestAttributes attrs =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());
        CountDownLatch ready = new CountDownLatch(workers);
        CountDownLatch start = new CountDownLatch(1);
        CountDownLatch done = new CountDownLatch(workers);
        AtomicInteger errors = new AtomicInteger();

        for (int i = 0; i < workers; i++) {
            Thread.ofVirtual().start(() -> {
                RequestContextHolder.setRequestAttributes(attrs);
                try {
                    ready.countDown();
                    assertTrue(start.await(5, TimeUnit.SECONDS));
                    scope.get("bean", Object::new);
                } catch (Throwable t) {
                    errors.incrementAndGet();
                } finally {
                    RequestContextHolder.resetRequestAttributes();
                    done.countDown();
                }
            });
        }

        assertTrue(ready.await(5, TimeUnit.SECONDS));
        start.countDown();
        assertTrue(done.await(10, TimeUnit.SECONDS));

        assertEquals(0, errors.get());
        assertScopeState(scope.stateForTesting(), 1, workers - 1);
        assertEquals(1, attrs.callbackRegistrations);
    }

    private static class RecordingServletRequestAttributes extends ServletRequestAttributes {

        protected int callbackRegistrations;
        protected Runnable callback;

        RecordingServletRequestAttributes(MockHttpServletRequest request) {
            super(request);
        }

        @Override
        public void registerDestructionCallback(String name, Runnable callback, int scope) {
            callbackRegistrations++;
            this.callback = callback;
            super.registerDestructionCallback(name, callback, scope);
        }

        void runCompletionCallback() {
            callback.run();
        }
    }

    private static final class FailingRegistrationServletRequestAttributes
            extends RecordingServletRequestAttributes {

        private FailingRegistrationServletRequestAttributes(MockHttpServletRequest request) {
            super(request);
        }

        @Override
        public void registerDestructionCallback(String name, Runnable callback, int scope) {
            callbackRegistrations++;
            this.callback = callback;
            throw new IllegalStateException("simulated callback registration failure");
        }
    }
}
