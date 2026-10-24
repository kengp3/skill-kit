package com.example.concurrentrequestscope.internal;

import java.time.Duration;
import java.util.Objects;

public final class ConcurrentRequestScopeSettings {

    private static final int DEFAULT_MAX_ACTIVE_REQUESTS = 20_000;
    private static final Duration DEFAULT_STALE_ENTRY_TTL = Duration.ofSeconds(120);
    private static final Duration DEFAULT_STALE_ENTRY_SCAN_INTERVAL = Duration.ofSeconds(30);

    private final int maxActiveRequests;
    private final boolean testingClearEnabled;
    private final boolean staleEntryCleanupEnabled;
    private final Duration staleEntryTtl;
    private final Duration staleEntryScanInterval;

    public ConcurrentRequestScopeSettings(int maxActiveRequests, boolean testingClearEnabled) {
        this(maxActiveRequests, testingClearEnabled, false,
                DEFAULT_STALE_ENTRY_TTL, DEFAULT_STALE_ENTRY_SCAN_INTERVAL);
    }

    public ConcurrentRequestScopeSettings(
            int maxActiveRequests,
            boolean testingClearEnabled,
            boolean staleEntryCleanupEnabled,
            Duration staleEntryTtl,
            Duration staleEntryScanInterval) {
        if (maxActiveRequests <= 0) {
            throw new IllegalArgumentException("maxActiveRequests must be positive");
        }
        Objects.requireNonNull(staleEntryTtl, "staleEntryTtl must not be null");
        Objects.requireNonNull(staleEntryScanInterval, "staleEntryScanInterval must not be null");
        if (!staleEntryTtl.isPositive()) {
            throw new IllegalArgumentException("staleEntryTtl must be positive");
        }
        if (!staleEntryScanInterval.isPositive()) {
            throw new IllegalArgumentException("staleEntryScanInterval must be positive");
        }
        this.maxActiveRequests = maxActiveRequests;
        this.testingClearEnabled = testingClearEnabled;
        this.staleEntryCleanupEnabled = staleEntryCleanupEnabled;
        this.staleEntryTtl = staleEntryTtl;
        this.staleEntryScanInterval = staleEntryScanInterval;
    }

    public static ConcurrentRequestScopeSettings defaults() {
        return new ConcurrentRequestScopeSettings(DEFAULT_MAX_ACTIVE_REQUESTS, false, true,
                DEFAULT_STALE_ENTRY_TTL, DEFAULT_STALE_ENTRY_SCAN_INTERVAL);
    }

    public int maxActiveRequests() {
        return maxActiveRequests;
    }

    public boolean testingClearEnabled() {
        return testingClearEnabled;
    }

    public boolean staleEntryCleanupEnabled() {
        return staleEntryCleanupEnabled;
    }

    public Duration staleEntryTtl() {
        return staleEntryTtl;
    }

    public Duration staleEntryScanInterval() {
        return staleEntryScanInterval;
    }

    @Override
    public boolean equals(Object o) {
        if (!(o instanceof ConcurrentRequestScopeSettings that)) {
            return false;
        }
        return maxActiveRequests == that.maxActiveRequests
                && testingClearEnabled == that.testingClearEnabled
                && staleEntryCleanupEnabled == that.staleEntryCleanupEnabled
                && staleEntryTtl.equals(that.staleEntryTtl)
                && staleEntryScanInterval.equals(that.staleEntryScanInterval);
    }

    @Override
    public int hashCode() {
        return Objects.hash(maxActiveRequests, testingClearEnabled,
                staleEntryCleanupEnabled, staleEntryTtl, staleEntryScanInterval);
    }
}
