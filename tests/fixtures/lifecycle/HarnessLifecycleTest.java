package com.example.concurrentrequestscope;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.config.Scope;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.support.GenericApplicationContext;
import org.springframework.mock.env.MockEnvironment;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

/** Observe cleanup effects; shared schedulers and virtual threads are valid. */
class HarnessLifecycleTest {
    @Test
    void closingOneContextPreservesAnotherContextsCleanup() throws Exception {
        AtomicInteger callbacks = new AtomicInteger();
        try (GenericApplicationContext first = cleanupContext();
             GenericApplicationContext second = cleanupContext()) {
            first.refresh();
            second.refresh();
            first.close();
            Scope scope = second.getBeanFactory().getRegisteredScope(
                    ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE);
            createOrphan(scope, callbacks);
            long deadline = System.nanoTime() + 3_000_000_000L;
            while (callbacks.get() == 0 && System.nanoTime() < deadline) Thread.sleep(10);
            assertEquals(1, callbacks.get(), "closing one context must preserve another's cleanup");
        } finally {
            RequestContextHolder.resetRequestAttributes();
        }
    }

    @Test
    void contextShutdownStopsItsBackgroundCleanup() throws Exception {
        AtomicInteger callbacks = new AtomicInteger();
        try (GenericApplicationContext context = cleanupContext()) {
            context.refresh();
            Scope scope = context.getBeanFactory().getRegisteredScope(
                    ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE);
            createOrphan(scope, callbacks);
            long deadline = System.nanoTime() + 3_000_000_000L;
            while (callbacks.get() == 0 && System.nanoTime() < deadline) Thread.sleep(10);
            assertEquals(1, callbacks.get(), "exercise real background cleanup before shutdown");
            long orphanCreated = System.nanoTime();
            createOrphan(scope, callbacks);
            assumeTrue(callbacks.get() == 1, "invalid observation: orphan expired before close");
            context.close();
            int atShutdown = callbacks.get();
            assumeTrue(System.nanoTime() - orphanCreated < 200_000_000L,
                    "invalid observation: shutdown crossed the orphan TTL");
            // A synchronous shutdown cleanup is valid. Later scans of this context are not.
            Thread.sleep(600);
            assertEquals(atShutdown, callbacks.get(), "no cleanup activity after context shutdown");
        } finally {
            RequestContextHolder.resetRequestAttributes();
        }
    }

    private static GenericApplicationContext cleanupContext() {
        AnnotationConfigApplicationContext context = new AnnotationConfigApplicationContext();
        context.setEnvironment(new MockEnvironment()
                        .withProperty("concurrent-request-scope.stale-entry-cleanup.enabled", "true")
                        .withProperty("concurrent-request-scope.stale-entry-cleanup.ttl", "200ms")
                        .withProperty("concurrent-request-scope.stale-entry-cleanup.scan-interval", "10ms"));
        context.register(EnabledCleanup.class);
        return context;
    }

    @Configuration(proxyBeanMethods = false)
    @EnableConcurrentRequestScope
    static class EnabledCleanup {
    }

    private static void createOrphan(Scope scope, AtomicInteger callbacks) {
        ServletRequestAttributes attributes = new ServletRequestAttributes(new MockHttpServletRequest());
        RequestContextHolder.setRequestAttributes(attributes);
        try {
            scope.get("probe", Object::new);
            scope.registerDestructionCallback("probe", callbacks::incrementAndGet);
        } finally {
            // Simulate the missing request-completion signal that the TTL cleaner handles.
            RequestContextHolder.resetRequestAttributes();
        }
    }
}
