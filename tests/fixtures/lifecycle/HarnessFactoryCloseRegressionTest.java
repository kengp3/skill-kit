package com.example.concurrentrequestscope;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.config.Scope;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Configuration;
import org.springframework.mock.env.MockEnvironment;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** Post-smoke diagnosis: a cooperative factory must not deadlock context shutdown. */
class HarnessFactoryCloseRegressionTest {
    @Test
    void factoryCanCloseItsContextWithoutLockUpgradeDeadlock() throws Exception {
        AnnotationConfigApplicationContext context = new AnnotationConfigApplicationContext();
        context.setEnvironment(new MockEnvironment()
                .withProperty("concurrent-request-scope.stale-entry-cleanup.enabled", "true")
                .withProperty("concurrent-request-scope.stale-entry-cleanup.ttl", "1h")
                .withProperty("concurrent-request-scope.stale-entry-cleanup.scan-interval", "1h"));
        context.register(Enabled.class);
        context.refresh();
        Scope scope = context.getBeanFactory().getRegisteredScope(
                ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE);
        CountDownLatch finished = new CountDownLatch(1);
        AtomicReference<Throwable> unexpected = new AtomicReference<>();
        // A failing lock implementation must not keep this isolated test JVM alive.
        Thread.ofPlatform().daemon().start(() -> {
            RequestContextHolder.setRequestAttributes(new ServletRequestAttributes(new MockHttpServletRequest()));
            try {
                scope.get("closing", () -> {
                    context.close();
                    return new Object();
                });
            } catch (IllegalStateException closedDuringCreation) {
                if (context.isActive()) unexpected.set(closedDuringCreation);
            } catch (Throwable failure) {
                unexpected.set(failure);
            } finally {
                RequestContextHolder.resetRequestAttributes();
                finished.countDown();
            }
        });
        assertTrue(finished.await(2, TimeUnit.SECONDS), "cooperative factory close must finish without lock upgrade deadlock");
        assertNull(unexpected.get());
        if (context.isActive()) context.close();
    }

    @Configuration(proxyBeanMethods = false)
    @EnableConcurrentRequestScope
    static class Enabled {
    }
}
