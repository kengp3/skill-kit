package com.example.concurrentrequestscope;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Scope;
import org.springframework.context.annotation.ScopedProxyMode;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.atomic.AtomicReference;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.catchThrowable;

@SpringJUnitConfig(ConcurrentRequestScopeUnsupportedConcurrencyTest.UnsupportedConcurrencyConfig.class)
@TestPropertySource(properties = "concurrent-request-scope.testing.clear-enabled=true")
class ConcurrentRequestScopeUnsupportedConcurrencyTest {

    @Autowired
    private UnsupportedScopedProbe scopedProbe;

    @Autowired
    private ConfigurableListableBeanFactory beanFactory;

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        registeredScope().clearForTesting();
    }

    @Test
    void unmanagedCompletableFutureIsUnsupported() {
        bindRequest();
        assertThat(scopedProbe.id()).isNotBlank();

        Throwable thrown = catchThrowable(() -> CompletableFuture.supplyAsync(scopedProbe::id).join());

        assertThat(thrown).isInstanceOf(CompletionException.class);
        assertThat(rootCause(thrown)).isInstanceOf(IllegalStateException.class);
    }

    @Test
    void rawVirtualThreadIsUnsupported() throws Exception {
        bindRequest();
        assertThat(scopedProbe.id()).isNotBlank();

        AtomicReference<Throwable> captured = new AtomicReference<>();
        Thread worker = Thread.ofVirtual().start(() -> {
            try {
                scopedProbe.id();
            } catch (Throwable throwable) {
                captured.set(throwable);
            }
        });
        worker.join(5_000);

        assertThat(worker.isAlive()).isFalse();
        assertThat(captured.get()).isNotNull();
        assertThat(rootCause(captured.get())).isInstanceOf(IllegalStateException.class);
    }

    private static void bindRequest() {
        RequestContextHolder.setRequestAttributes(new ServletRequestAttributes(new MockHttpServletRequest()));
    }

    private ConcurrentRequestScope registeredScope() {
        return (ConcurrentRequestScope) beanFactory.getRegisteredScope(
                ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE);
    }

    private static Throwable rootCause(Throwable throwable) {
        Throwable current = throwable;
        while (current.getCause() != null) {
            current = current.getCause();
        }
        return current;
    }

    @Configuration(proxyBeanMethods = false)
    @EnableConcurrentRequestScope
    static class UnsupportedConcurrencyConfig {

        @Bean
        @Scope(value = ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE, proxyMode = ScopedProxyMode.TARGET_CLASS)
        UnsupportedScopedProbe unsupportedScopedProbe() {
            return new UnsupportedScopedProbe();
        }
    }

    static class UnsupportedScopedProbe {

        private final String id = UUID.randomUUID().toString();

        String id() {
            return id;
        }
    }
}
