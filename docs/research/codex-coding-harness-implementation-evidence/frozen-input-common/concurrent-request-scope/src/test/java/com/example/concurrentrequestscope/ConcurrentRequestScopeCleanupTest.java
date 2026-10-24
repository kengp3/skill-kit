package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCleanupException;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.web.context.request.RequestAttributes;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.concurrent.atomic.AtomicInteger;

import static com.example.concurrentrequestscope.support.ConcurrentRequestScopeStateAssertions.assertBaseline;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ConcurrentRequestScopeCleanupTest {

    private ConcurrentRequestScope scope;

    @BeforeEach
    void setUp() {
        scope = new ConcurrentRequestScope(new ConcurrentRequestScopeSettings(10, true));
    }

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        scope.clearForTesting();
    }

    @Test
    void entryCreationRegistersExactlyOneRequestCompletionCallback() {
        RecordingServletRequestAttributes attrs =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);

        scope.get("first", Object::new);
        scope.get("second", Object::new);

        assertEquals(1, attrs.callbackRegistrations);
        assertEquals(ConcurrentRequestScope.class.getName() + ".cleanup", attrs.callbackName);
        assertEquals(RequestAttributes.SCOPE_REQUEST, attrs.callbackScope);
    }

    @Test
    void requestTimeCallbackRegistrationFailureRollsBackEntryAndCapacity() {
        FailingRegistrationServletRequestAttributes attrs =
                new FailingRegistrationServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);

        assertThrows(ConcurrentRequestScopeCleanupException.class, () -> scope.get("bean", Object::new));

        assertEquals(1, attrs.callbackRegistrations);
        assertBaseline(scope.stateForTesting());
    }

    @Test
    void registeredCallbackRunsOnRequestCompletionCleanup() {
        RecordingServletRequestAttributes attrs =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);
        AtomicInteger callbackRuns = new AtomicInteger();

        scope.get("bean", Object::new);
        scope.registerDestructionCallback("bean", callbackRuns::incrementAndGet);
        attrs.runCompletionCallback();

        assertEquals(1, callbackRuns.get());
        assertBaseline(scope.stateForTesting());
    }

    @Test
    void removePreventsThatBeanCallbackFromRunning() {
        RecordingServletRequestAttributes attrs =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);
        AtomicInteger callbackRuns = new AtomicInteger();
        Object bean = scope.get("bean", Object::new);
        scope.registerDestructionCallback("bean", callbackRuns::incrementAndGet);

        assertSame(bean, scope.remove("bean"));
        attrs.runCompletionCallback();

        assertEquals(0, callbackRuns.get());
        assertBaseline(scope.stateForTesting());
    }

    @Test
    void removeSuppressesOldCallbackButFreshCreationCallbackRuns() {
        RecordingServletRequestAttributes attrs =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);
        AtomicInteger removedCallbackRuns = new AtomicInteger();
        AtomicInteger freshCallbackRuns = new AtomicInteger();
        Object original = scope.get("bean", Object::new);
        scope.registerDestructionCallback("bean", removedCallbackRuns::incrementAndGet);

        assertSame(original, scope.remove("bean"));
        Object fresh = scope.get("bean", Object::new);
        scope.registerDestructionCallback("bean", freshCallbackRuns::incrementAndGet);
        attrs.runCompletionCallback();

        assertNotSame(original, fresh);
        assertEquals(0, removedCallbackRuns.get());
        assertEquals(1, freshCallbackRuns.get());
        assertBaseline(scope.stateForTesting());
    }

    @Test
    void callbackFailureDoesNotPreventRemainingCallbacksOrCapacityRecovery() {
        RecordingServletRequestAttributes attrs =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);
        AtomicInteger survivingCallbackRuns = new AtomicInteger();

        scope.get("a", Object::new);
        scope.get("b", Object::new);
        scope.registerDestructionCallback("a", () -> {
            throw new IllegalStateException("callback failed");
        });
        scope.registerDestructionCallback("b", survivingCallbackRuns::incrementAndGet);
        attrs.runCompletionCallback();

        assertEquals(1, survivingCallbackRuns.get());
        assertEquals(1, scope.stateForTesting().cleanupFailureCount());
        assertBaseline(scope.stateForTesting());
    }

    static class RecordingServletRequestAttributes extends ServletRequestAttributes {

        protected int callbackRegistrations;
        protected String callbackName;
        protected Runnable callback;
        protected int callbackScope = -1;

        RecordingServletRequestAttributes(MockHttpServletRequest request) {
            super(request);
        }

        @Override
        public void registerDestructionCallback(String name, Runnable callback, int scope) {
            callbackRegistrations++;
            callbackName = name;
            this.callback = callback;
            callbackScope = scope;
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
            callbackName = name;
            this.callback = callback;
            callbackScope = scope;
            throw new IllegalStateException("simulated callback registration failure");
        }
    }
}
