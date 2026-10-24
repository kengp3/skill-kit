package com.example.concurrentrequestscope.internal;

import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeBackdoorException;

import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiConsumer;
import java.util.function.LongSupplier;

public final class ConcurrentRequestScopeState {

    private final ConcurrentRequestScopeSettings settings;
    private final ConcurrentHashMap<Object, ConcurrentRequestScopeEntry> entries = new ConcurrentHashMap<>(512);
    private final Semaphore capacity;
    private final LongSupplier nanoTimeSource;
    private final AtomicLong conversationIdCounter = new AtomicLong();
    private final AtomicLong cleanupFailureCounter = new AtomicLong();
    private final AtomicLong staleEntryCleanupCounter = new AtomicLong();
    private final Object capacityResetLock = new Object();

    public ConcurrentRequestScopeState(ConcurrentRequestScopeSettings settings) {
        this(settings, System::nanoTime);
    }

    public ConcurrentRequestScopeState(ConcurrentRequestScopeSettings settings, LongSupplier nanoTimeSource) {
        this.settings = Objects.requireNonNull(settings, "settings must not be null");
        this.nanoTimeSource = Objects.requireNonNull(nanoTimeSource, "nanoTimeSource must not be null");
        this.capacity = new Semaphore(settings.maxActiveRequests());
    }

    public ConcurrentRequestScopeSettings settings() {
        return settings;
    }

    public boolean tryAcquireCapacity() {
        return capacity.tryAcquire();
    }

    public void releaseCapacity() {
        capacity.release();
    }

    public int availableCapacity() {
        return capacity.availablePermits();
    }

    public long activeEntryCount() {
        return entries.mappingCount();
    }

    public long nextConversationSequence() {
        return conversationIdCounter.incrementAndGet();
    }

    public long nowNanos() {
        return nanoTimeSource.getAsLong();
    }

    public ConcurrentRequestScopeEntry createEntry() {
        return new ConcurrentRequestScopeEntry(nextConversationSequence(), nowNanos());
    }

    public void recordCleanupFailures(long failures) {
        if (failures > 0) {
            cleanupFailureCounter.addAndGet(failures);
        }
    }

    public long cleanupFailureCount() {
        return cleanupFailureCounter.get();
    }

    public void recordStaleEntryCleanup() {
        staleEntryCleanupCounter.incrementAndGet();
    }

    public long staleEntryCleanupCount() {
        return staleEntryCleanupCounter.get();
    }

    public ConcurrentRequestScopeEntry getEntry(Object key) {
        return entries.get(key);
    }

    public ConcurrentRequestScopeEntry putEntryIfAbsent(Object key, ConcurrentRequestScopeEntry entry) {
        Objects.requireNonNull(key, "key must not be null");
        Objects.requireNonNull(entry, "entry must not be null");
        return entries.putIfAbsent(key, entry);
    }

    public boolean removeEntryIfSame(Object key, ConcurrentRequestScopeEntry entry) {
        Objects.requireNonNull(key, "key must not be null");
        Objects.requireNonNull(entry, "entry must not be null");
        return entries.remove(key, entry);
    }

    public boolean capacityInvariantHolds() {
        return availableCapacity() + activeEntryCount() == settings.maxActiveRequests();
    }

    public int forEachStaleEntry(long ttlNanos, BiConsumer<Object, ConcurrentRequestScopeEntry> cleanup) {
        Objects.requireNonNull(cleanup, "cleanup must not be null");
        long nowNanos = nowNanos();
        AtomicLong candidates = new AtomicLong();
        entries.forEach((key, entry) -> {
            if (entry.staleAt(nowNanos, ttlNanos)) {
                candidates.incrementAndGet();
                cleanup.accept(key, entry);
            }
        });
        return Math.toIntExact(candidates.get());
    }

    public void clearForTesting() {
        if (!settings.testingClearEnabled()) {
            throw new ConcurrentRequestScopeBackdoorException(
                    "Test cleanup is disabled. Set concurrent-request-scope.testing.clear-enabled=true in test wiring.");
        }
        entries.clear();
        conversationIdCounter.set(0);
        cleanupFailureCounter.set(0);
        staleEntryCleanupCounter.set(0);
        synchronized (capacityResetLock) {
            capacity.drainPermits();
            capacity.release(settings.maxActiveRequests());
        }
    }
}
