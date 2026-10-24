package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeBeanFactoryPostProcessor;
import org.junit.jupiter.api.Test;
import org.springframework.context.support.GenericApplicationContext;
import org.springframework.mock.env.MockEnvironment;

import java.util.Set;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** External lifecycle check: no private fields or required close() implementation. */
class HarnessLifecycleTest {
    @Test
    void contextShutdownReleasesItsBackgroundWorkers() throws Exception {
        Set<Long> existing = Thread.getAllStackTraces().keySet().stream()
                .map(Thread::threadId).collect(Collectors.toSet());
        Set<Thread> started;
        try (GenericApplicationContext context = new GenericApplicationContext()) {
            context.addBeanFactoryPostProcessor(new ConcurrentRequestScopeBeanFactoryPostProcessor(
                    new MockEnvironment()
                            .withProperty("concurrent-request-scope.stale-entry-cleanup.enabled", "true")
                            .withProperty("concurrent-request-scope.stale-entry-cleanup.scan-interval", "10ms")));
            context.refresh();
            started = Thread.getAllStackTraces().keySet().stream()
                    .filter(thread -> thread.isAlive() && !existing.contains(thread.threadId()))
                    .collect(Collectors.toSet());
            assertFalse(started.isEmpty(), "background cleanup must be exercised");
        }
        long deadline = System.nanoTime() + 3_000_000_000L;
        for (Thread worker : started) {
            long remaining = deadline - System.nanoTime();
            if (remaining > 0) worker.join(Math.max(1, remaining / 1_000_000L));
        }
        assertTrue(started.stream().noneMatch(Thread::isAlive),
                "context-owned background workers must stop after shutdown: " + started);
    }
}
