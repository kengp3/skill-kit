package com.example.concurrentrequestscope.internal;

import org.springframework.beans.factory.ObjectFactory;
import org.springframework.beans.factory.BeanCurrentlyInCreationException;

import java.util.HashSet;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiConsumer;

public final class ConcurrentRequestScopeEntry {

    private final ConcurrentHashMap<String, BeanSlot> slots = new ConcurrentHashMap<>();
    private final DestructionCallbackRegistry destructionCallbacks = new DestructionCallbackRegistry();
    private final String conversationId;
    private final long createdAtNanos;
    private final AtomicLong lastAccessAtNanos;
    private final ThreadLocal<Set<String>> creatingBeans = ThreadLocal.withInitial(HashSet::new);

    public ConcurrentRequestScopeEntry(long conversationSequence) {
        this(conversationSequence, System.nanoTime());
    }

    public ConcurrentRequestScopeEntry(long conversationSequence, long createdAtNanos) {
        this.conversationId = Long.toString(conversationSequence);
        this.createdAtNanos = createdAtNanos;
        this.lastAccessAtNanos = new AtomicLong(createdAtNanos);
    }

    public String conversationId() {
        return conversationId;
    }

    public long createdAtNanos() {
        return createdAtNanos;
    }

    public long lastAccessAtNanos() {
        return lastAccessAtNanos.get();
    }

    public void touch(long nowNanos) {
        lastAccessAtNanos.accumulateAndGet(nowNanos, Math::max);
    }

    public boolean staleAt(long nowNanos, long ttlNanos) {
        return nowNanos - lastAccessAtNanos.get() >= ttlNanos;
    }

    public Object getOrCreateBean(String name, ObjectFactory<?> objectFactory) {
        Objects.requireNonNull(name, "bean name must not be null");
        Objects.requireNonNull(objectFactory, "objectFactory must not be null");
        Set<String> creating = creatingBeans.get();
        if (!creating.add(name)) {
            throw new BeanCurrentlyInCreationException(name,
                    "[ConcurrentRequestScope] detected circular creation for bean '" + name + "'");
        }
        BeanSlot slot = slots.computeIfAbsent(name, BeanSlot::new);
        try {
            return slot.getOrCreate(objectFactory);
        } catch (RuntimeException | Error e) {
            if (!slot.initialized()) {
                slots.remove(name, slot);
            }
            throw e;
        } finally {
            creating.remove(name);
            if (creating.isEmpty()) {
                creatingBeans.remove();
            }
        }
    }

    public Object removeBean(String name) {
        Objects.requireNonNull(name, "bean name must not be null");
        destructionCallbacks.remove(name);
        BeanSlot removed = slots.remove(name);
        return removed != null ? removed.valueOrNull() : null;
    }

    public void registerDestructionCallback(String name, Runnable callback) {
        destructionCallbacks.register(name, callback);
    }

    public int runDestructionCallbacks(BiConsumer<String, Throwable> failureHandler) {
        return destructionCallbacks.runBestEffort(failureHandler);
    }
}
