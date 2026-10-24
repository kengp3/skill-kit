package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeSnapshotException;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.concurrent.atomic.AtomicInteger;

import static com.example.concurrentrequestscope.support.ConcurrentRequestScopeStateAssertions.assertBaseline;
import static com.example.concurrentrequestscope.support.ConcurrentRequestScopeStateAssertions.assertScopeState;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ConcurrentRequestScopeSnapshotTest {

    private ConcurrentRequestScope scope;

    @BeforeEach
    void setUp() {
        scope = new ConcurrentRequestScope(new ConcurrentRequestScopeSettings(5, true));
    }

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        scope.clearForTesting();
    }

    @Test
    void missingEntrySnapshotRejectsBeforeEntryPermitOrCallbackSideEffects() {
        RecordingSnapshotServletRequestAttributes attrs =
                new RecordingSnapshotServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);

        assertThrows(ConcurrentRequestScopeSnapshotException.class, () -> scope.get("bean", Object::new));

        assertBaseline(scope.stateForTesting());
        assertEquals(0, attrs.callbackRegistrations);
    }

    @Test
    void existingEntrySnapshotCanUseThePrewarmedRequestEntry() {
        MockHttpServletRequest request = new MockHttpServletRequest();
        RecordingServletRequestAttributes ownerAttrs = new RecordingServletRequestAttributes(request);
        Object ownerBean = new Object();
        Object workerBean = new Object();
        AtomicInteger workerCallbackRuns = new AtomicInteger();

        RequestContextHolder.setRequestAttributes(ownerAttrs);
        assertSame(ownerBean, scope.get("owner", () -> ownerBean));

        RecordingSnapshotServletRequestAttributes snapshotAttrs =
                new RecordingSnapshotServletRequestAttributes(request);
        RequestContextHolder.setRequestAttributes(snapshotAttrs);

        assertSame(ownerBean, scope.get("owner", Object::new));
        assertSame(workerBean, scope.get("worker", () -> workerBean));
        scope.registerDestructionCallback("worker", workerCallbackRuns::incrementAndGet);
        assertScopeState(scope.stateForTesting(), 1, 4);
        assertEquals(1, ownerAttrs.callbackRegistrations);
        assertEquals(0, snapshotAttrs.callbackRegistrations);

        ownerAttrs.runCompletionCallback();

        assertEquals(1, workerCallbackRuns.get());
        assertBaseline(scope.stateForTesting());
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

    private static final class RecordingSnapshotServletRequestAttributes
            extends RecordingServletRequestAttributes {

        private RecordingSnapshotServletRequestAttributes(MockHttpServletRequest request) {
            super(request);
        }
    }
}
