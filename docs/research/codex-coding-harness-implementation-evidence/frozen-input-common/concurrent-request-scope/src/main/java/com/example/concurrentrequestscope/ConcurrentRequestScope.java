package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCapacityException;
import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCleanupException;
import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeSnapshotException;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeEntry;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeState;
import com.example.concurrentrequestscope.internal.ScopeKeyResolver;
import org.springframework.beans.factory.ObjectFactory;
import org.springframework.beans.factory.config.Scope;
import org.springframework.web.context.request.RequestAttributes;
import org.springframework.web.context.request.RequestContextHolder;

import java.time.Duration;
import java.util.Objects;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;

public class ConcurrentRequestScope implements Scope {

    private static final System.Logger LOGGER = System.getLogger(ConcurrentRequestScope.class.getName());
    private static final String CLEANUP_CALLBACK_NAME =
            ConcurrentRequestScope.class.getName() + ".cleanup";

    private final ConcurrentRequestScopeState state;
    private final ScopeKeyResolver keyResolver;
    private final ScheduledExecutorService staleEntryCleanupExecutor;

    public ConcurrentRequestScope() {
        this(ConcurrentRequestScopeSettings.defaults());
    }

    public ConcurrentRequestScope(ConcurrentRequestScopeSettings settings) {
        this(new ConcurrentRequestScopeState(settings), new ScopeKeyResolver(), true);
    }

    public ConcurrentRequestScope(ConcurrentRequestScopeState state, ScopeKeyResolver keyResolver) {
        this(state, keyResolver, false);
    }

    private ConcurrentRequestScope(
            ConcurrentRequestScopeState state,
            ScopeKeyResolver keyResolver,
            boolean startStaleEntryCleanup) {
        this.state = Objects.requireNonNull(state, "state must not be null");
        this.keyResolver = Objects.requireNonNull(keyResolver, "keyResolver must not be null");
        this.staleEntryCleanupExecutor = startStaleEntryCleanup ? startStaleEntryCleanup() : null;
    }

    @Override
    public Object get(String name, ObjectFactory<?> objectFactory) {
        Objects.requireNonNull(name, "bean name must not be null");
        Objects.requireNonNull(objectFactory, "objectFactory must not be null");
        ConcurrentRequestScopeEntry entry = getOrCreateEntry(RequestContextHolder.currentRequestAttributes());
        return entry.getOrCreateBean(name, objectFactory);
    }

    @Override
    public Object remove(String name) {
        RequestAttributes attrs = RequestContextHolder.getRequestAttributes();
        if (attrs == null) {
            return null;
        }
        ConcurrentRequestScopeEntry entry = state.getEntry(keyResolver.scopeKey(attrs));
        return entry != null ? entry.removeBean(name) : null;
    }

    @Override
    public void registerDestructionCallback(String name, Runnable callback) {
        Objects.requireNonNull(name, "bean name must not be null");
        Objects.requireNonNull(callback, "destruction callback must not be null");
        RequestAttributes attrs = RequestContextHolder.currentRequestAttributes();
        ConcurrentRequestScopeEntry entry = state.getEntry(keyResolver.scopeKey(attrs));
        if (entry == null) {
            throw new IllegalStateException(
                    "[ConcurrentRequestScope] cannot register destruction callback before request entry exists");
        }
        entry.registerDestructionCallback(name, callback);
    }

    @Override
    public Object resolveContextualObject(String key) {
        RequestAttributes attrs = RequestContextHolder.currentRequestAttributes();
        return attrs.resolveReference(key);
    }

    @Override
    public String getConversationId() {
        RequestAttributes attrs = RequestContextHolder.getRequestAttributes();
        if (attrs == null) {
            return null;
        }
        ConcurrentRequestScopeEntry entry = state.getEntry(keyResolver.scopeKey(attrs));
        return entry != null ? entry.conversationId() : null;
    }

    void clearForTesting() {
        state.clearForTesting();
    }

    ConcurrentRequestScopeState stateForTesting() {
        return state;
    }

    Object scopeKeyForTesting(RequestAttributes attrs) {
        return keyResolver.scopeKey(attrs);
    }

    void cleanupScopeEntryForTesting(Object key, ConcurrentRequestScopeEntry expected) {
        cleanupScopeEntry(key, expected);
    }

    int cleanupStaleEntriesForTesting() {
        return cleanupStaleEntries();
    }

    private ConcurrentRequestScopeEntry getOrCreateEntry(RequestAttributes attrs) {
        Object key = keyResolver.scopeKey(attrs);
        ConcurrentRequestScopeEntry existing = state.getEntry(key);
        if (existing != null) {
            existing.touch(state.nowNanos());
            return existing;
        }
        if (keyResolver.isSnapshot(attrs)) {
            throw new ConcurrentRequestScopeSnapshotException(
                    "[ConcurrentRequestScope] missing request entry from propagated snapshot attributes is rejected: "
                            + attrs.getClass().getSimpleName());
        }
        if (!state.tryAcquireCapacity()) {
            throw new ConcurrentRequestScopeCapacityException(
                    "[ConcurrentRequestScope] capacity limit reached: max active requests = "
                            + state.settings().maxActiveRequests());
        }
        ConcurrentRequestScopeEntry candidate = state.createEntry();
        ConcurrentRequestScopeEntry winner = state.putEntryIfAbsent(key, candidate);
        if (winner != null) {
            state.releaseCapacity();
            winner.touch(state.nowNanos());
            return winner;
        }
        try {
            attrs.registerDestructionCallback(
                    CLEANUP_CALLBACK_NAME,
                    () -> cleanupScopeEntry(key, candidate),
                    RequestAttributes.SCOPE_REQUEST);
        } catch (RuntimeException e) {
            if (state.removeEntryIfSame(key, candidate)) {
                state.releaseCapacity();
            }
            throw new ConcurrentRequestScopeCleanupException(
                    "[ConcurrentRequestScope] cleanup callback registration failed for conversation "
                            + candidate.conversationId(),
                    e);
        }
        return candidate;
    }

    private ScheduledExecutorService startStaleEntryCleanup() {
        ConcurrentRequestScopeSettings settings = state.settings();
        if (!settings.staleEntryCleanupEnabled()) {
            return null;
        }

        ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor(staleCleanerThreadFactory());
        Duration scanInterval = settings.staleEntryScanInterval();
        executor.scheduleWithFixedDelay(
                this::cleanupStaleEntriesSafely,
                scanInterval.toNanos(),
                scanInterval.toNanos(),
                TimeUnit.NANOSECONDS);
        return executor;
    }

    private static ThreadFactory staleCleanerThreadFactory() {
        return runnable -> {
            Thread thread = Thread.ofPlatform()
                    .name("concurrent-request-scope-stale-cleaner")
                    .unstarted(runnable);
            thread.setDaemon(true);
            return thread;
        };
    }

    private void cleanupStaleEntriesSafely() {
        try {
            cleanupStaleEntries();
        } catch (RuntimeException e) {
            LOGGER.log(System.Logger.Level.ERROR,
                    "[ConcurrentRequestScope] stale entry cleanup scan failed",
                    e);
        }
    }

    private int cleanupStaleEntries() {
        ConcurrentRequestScopeSettings settings = state.settings();
        if (!settings.staleEntryCleanupEnabled()) {
            return 0;
        }
        long ttlNanos = settings.staleEntryTtl().toNanos();
        return state.forEachStaleEntry(ttlNanos, this::cleanupStaleEntry);
    }

    private void cleanupStaleEntry(Object key, ConcurrentRequestScopeEntry expected) {
        if (!state.removeEntryIfSame(key, expected)) {
            return;
        }
        try {
            int failures = expected.runDestructionCallbacks((name, thrown) ->
                    LOGGER.log(System.Logger.Level.ERROR,
                            "[ConcurrentRequestScope] destruction callback failed during stale cleanup for bean '"
                                    + name + "'",
                            thrown));
            state.recordCleanupFailures(failures);
            state.recordStaleEntryCleanup();
            LOGGER.log(System.Logger.Level.WARNING,
                    "[ConcurrentRequestScope] stale request entry cleaned up for conversation "
                            + expected.conversationId());
        } finally {
            state.releaseCapacity();
        }
    }

    private void cleanupScopeEntry(Object key, ConcurrentRequestScopeEntry expected) {
        if (!state.removeEntryIfSame(key, expected)) {
            return;
        }
        try {
            int failures = expected.runDestructionCallbacks((name, thrown) ->
                    LOGGER.log(System.Logger.Level.ERROR,
                            "[ConcurrentRequestScope] destruction callback failed for bean '" + name + "'",
                            thrown));
            state.recordCleanupFailures(failures);
        } finally {
            state.releaseCapacity();
        }
    }
}
