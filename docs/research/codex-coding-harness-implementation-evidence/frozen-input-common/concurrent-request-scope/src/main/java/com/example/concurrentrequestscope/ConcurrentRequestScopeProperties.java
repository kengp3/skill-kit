package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.time.Duration;

@ConfigurationProperties("concurrent-request-scope")
public class ConcurrentRequestScopeProperties {

    private int maxActiveRequests = 20_000;

    private final Testing testing = new Testing();
    private final StaleEntryCleanup staleEntryCleanup = new StaleEntryCleanup();

    public int getMaxActiveRequests() {
        return maxActiveRequests;
    }

    public void setMaxActiveRequests(int maxActiveRequests) {
        this.maxActiveRequests = maxActiveRequests;
    }

    public Testing getTesting() {
        return testing;
    }

    public StaleEntryCleanup getStaleEntryCleanup() {
        return staleEntryCleanup;
    }

    public ConcurrentRequestScopeSettings toSettings() {
        return new ConcurrentRequestScopeSettings(
                maxActiveRequests,
                testing.clearEnabled,
                staleEntryCleanup.enabled,
                staleEntryCleanup.ttl,
                staleEntryCleanup.scanInterval);
    }

    public static final class Testing {

        private boolean clearEnabled;

        public boolean isClearEnabled() {
            return clearEnabled;
        }

        public void setClearEnabled(boolean clearEnabled) {
            this.clearEnabled = clearEnabled;
        }
    }

    public static final class StaleEntryCleanup {

        private boolean enabled = true;
        private Duration ttl = Duration.ofSeconds(120);
        private Duration scanInterval = Duration.ofSeconds(30);

        public boolean isEnabled() {
            return enabled;
        }

        public void setEnabled(boolean enabled) {
            this.enabled = enabled;
        }

        public Duration getTtl() {
            return ttl;
        }

        public void setTtl(Duration ttl) {
            this.ttl = ttl;
        }

        public Duration getScanInterval() {
            return scanInterval;
        }

        public void setScanInterval(Duration scanInterval) {
            this.scanInterval = scanInterval;
        }
    }
}
