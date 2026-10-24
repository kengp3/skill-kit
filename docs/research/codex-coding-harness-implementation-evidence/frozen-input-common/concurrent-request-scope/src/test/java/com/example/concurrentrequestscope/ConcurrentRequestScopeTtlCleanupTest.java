package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeSnapshotException;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeEntry;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeState;
import com.example.concurrentrequestscope.internal.ScopeKeyResolver;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.time.Duration;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.LongSupplier;

import static com.example.concurrentrequestscope.support.ConcurrentRequestScopeStateAssertions.assertBaseline;
import static com.example.concurrentrequestscope.support.ConcurrentRequestScopeStateAssertions.assertScopeState;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ConcurrentRequestScopeTtlCleanupTest {

    private static final Duration TTL = Duration.ofSeconds(10);

    private ManualNanoTime nanoTime;
    private ConcurrentRequestScopeState state;
    private ConcurrentRequestScope scope;

    @BeforeEach
    void setUp() {
        nanoTime = new ManualNanoTime();
        state = new ConcurrentRequestScopeState(
                new ConcurrentRequestScopeSettings(5, true, true, TTL, Duration.ofSeconds(1)),
                nanoTime);
        scope = new ConcurrentRequestScope(state, new ScopeKeyResolver());
    }

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        scope.clearForTesting();
    }

    @Test
    void expiredEntryCleanupReturnsActiveEntriesAndCapacityToBaseline() {
        RecordingServletRequestAttributes attrs =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());
        AtomicInteger callbackRuns = new AtomicInteger();
        RequestContextHolder.setRequestAttributes(attrs);

        scope.get("bean", Object::new);
        scope.registerDestructionCallback("bean", callbackRuns::incrementAndGet);
        assertScopeState(state, 1, 4);

        nanoTime.advance(TTL.plusNanos(1));
        assertEquals(1, scope.cleanupStaleEntriesForTesting());

        assertEquals(1, callbackRuns.get());
        assertEquals(1, state.staleEntryCleanupCount());
        assertBaseline(state);
    }

    @Test
    void normalCleanupAndTtlCleanupRaceDoesNotOverReleaseCapacity() {
        RecordingServletRequestAttributes attrs =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);

        scope.get("bean", Object::new);
        attrs.runCompletionCallback();
        nanoTime.advance(TTL.plusNanos(1));

        assertEquals(0, scope.cleanupStaleEntriesForTesting());
        assertBaseline(state);
    }

    @Test
    void staleExpectedEntryCannotRemoveNewerEntryForSameKey() {
        RecordingServletRequestAttributes attrs =
                new RecordingServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attrs);
        Object key = scope.scopeKeyForTesting(attrs);

        scope.get("old", Object::new);
        ConcurrentRequestScopeEntry oldEntry = state.getEntry(key);
        attrs.runCompletionCallback();

        scope.get("new", Object::new);
        ConcurrentRequestScopeEntry newEntry = state.getEntry(key);

        scope.cleanupScopeEntryForTesting(key, oldEntry);

        assertSame(newEntry, state.getEntry(key));
        assertScopeState(state, 1, 4);
    }

    @Test
    void staleEntryCleanupKeepsMissingEntrySnapshotFailSecure() {
        MockHttpServletRequest request = new MockHttpServletRequest();
        RecordingServletRequestAttributes ownerAttrs = new RecordingServletRequestAttributes(request);
        RequestContextHolder.setRequestAttributes(ownerAttrs);

        scope.get("bean", Object::new);
        nanoTime.advance(TTL.plusNanos(1));
        scope.cleanupStaleEntriesForTesting();

        RequestContextHolder.setRequestAttributes(new RecordingSnapshotServletRequestAttributes(request));

        assertThrows(ConcurrentRequestScopeSnapshotException.class, () -> scope.get("lateWorker", Object::new));
        assertBaseline(state);
    }

    private static final class ManualNanoTime implements LongSupplier {

        private long now;

        @Override
        public long getAsLong() {
            return now;
        }

        void advance(Duration duration) {
            now += duration.toNanos();
        }
    }

    private static class RecordingServletRequestAttributes extends ServletRequestAttributes {

        private Runnable callback;

        RecordingServletRequestAttributes(MockHttpServletRequest request) {
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

    private static final class RecordingSnapshotServletRequestAttributes extends RecordingServletRequestAttributes {

        private RecordingSnapshotServletRequestAttributes(MockHttpServletRequest request) {
            super(request);
        }
    }
}
