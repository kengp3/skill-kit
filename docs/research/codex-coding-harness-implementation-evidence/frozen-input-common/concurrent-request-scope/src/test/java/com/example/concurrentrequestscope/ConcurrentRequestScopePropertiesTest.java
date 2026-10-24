package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import org.junit.jupiter.api.Test;
import org.springframework.boot.context.properties.bind.Binder;
import org.springframework.mock.env.MockEnvironment;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ConcurrentRequestScopePropertiesTest {

    @Test
    void defaultsMatchProductionContract() {
        ConcurrentRequestScopeSettings settings = new ConcurrentRequestScopeProperties().toSettings();

        assertThat(settings.maxActiveRequests()).isEqualTo(20_000);
        assertThat(settings.testingClearEnabled()).isFalse();
        assertThat(settings.staleEntryCleanupEnabled()).isTrue();
        assertThat(settings.staleEntryTtl()).isEqualTo(Duration.ofSeconds(120));
        assertThat(settings.staleEntryScanInterval()).isEqualTo(Duration.ofSeconds(30));
    }

    @Test
    void bindsSpringProperties() {
        MockEnvironment environment = new MockEnvironment()
                .withProperty("concurrent-request-scope.max-active-requests", "123")
                .withProperty("concurrent-request-scope.testing.clear-enabled", "true")
                .withProperty("concurrent-request-scope.stale-entry-cleanup.enabled", "false")
                .withProperty("concurrent-request-scope.stale-entry-cleanup.ttl", "90s")
                .withProperty("concurrent-request-scope.stale-entry-cleanup.scan-interval", "15s");

        ConcurrentRequestScopeProperties properties = Binder.get(environment)
                .bind("concurrent-request-scope", ConcurrentRequestScopeProperties.class)
                .orElseGet(ConcurrentRequestScopeProperties::new);

        ConcurrentRequestScopeSettings settings = properties.toSettings();
        assertThat(settings.maxActiveRequests()).isEqualTo(123);
        assertThat(settings.testingClearEnabled()).isTrue();
        assertThat(settings.staleEntryCleanupEnabled()).isFalse();
        assertThat(settings.staleEntryTtl()).isEqualTo(Duration.ofSeconds(90));
        assertThat(settings.staleEntryScanInterval()).isEqualTo(Duration.ofSeconds(15));
    }

    @Test
    void settingsRejectNonPositiveStaleCleanupDurations() {
        assertThrows(IllegalArgumentException.class,
                () -> new ConcurrentRequestScopeSettings(
                        10, false, true, Duration.ZERO, Duration.ofSeconds(1)));
        assertThrows(IllegalArgumentException.class,
                () -> new ConcurrentRequestScopeSettings(
                        10, false, true, Duration.ofSeconds(1), Duration.ZERO));
    }
}
