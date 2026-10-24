package com.example.concurrentrequestscope.internal;

import org.springframework.beans.factory.ObjectFactory;

import java.util.Objects;

public final class BeanSlot {

    private final String name;
    private boolean creating;
    private boolean initialized;
    private Object value;
    private Throwable failure;

    public BeanSlot(String name) {
        this.name = Objects.requireNonNull(name, "bean name must not be null");
    }

    public Object getOrCreate(ObjectFactory<?> objectFactory) {
        Objects.requireNonNull(objectFactory, "objectFactory must not be null");
        synchronized (this) {
            if (initialized) {
                return value;
            }
            if (creating) {
                return awaitResult();
            }
            creating = true;
            failure = null;
        }

        Object created = null;
        Throwable thrown = null;
        try {
            created = objectFactory.getObject();
            if (created == null) {
                throw new IllegalStateException(
                        "[ConcurrentRequestScope] objectFactory returned null for bean '" + name + "'");
            }
            return completeSuccess(created);
        } catch (Throwable t) {
            thrown = t;
            completeFailure(t);
            throw rethrow(t);
        } finally {
            if (thrown != null) {
                // The failure is stored only to wake current waiters with the same outcome.
                // The owning entry removes failed slots from the map so future calls retry.
            }
        }
    }

    public synchronized Object valueOrNull() {
        return initialized ? value : null;
    }

    public synchronized boolean initialized() {
        return initialized;
    }

    private Object awaitResult() {
        while (creating) {
            try {
                wait();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new IllegalStateException(
                        "[ConcurrentRequestScope] interrupted while waiting for bean '" + name + "'", e);
            }
        }
        if (initialized) {
            return value;
        }
        if (failure != null) {
            throw rethrow(failure);
        }
        throw new IllegalStateException(
                "[ConcurrentRequestScope] bean slot for '" + name + "' completed without value or failure");
    }

    private synchronized Object completeSuccess(Object created) {
        value = created;
        initialized = true;
        creating = false;
        notifyAll();
        return created;
    }

    private synchronized void completeFailure(Throwable thrown) {
        failure = thrown;
        initialized = false;
        creating = false;
        notifyAll();
    }

    private static RuntimeException rethrow(Throwable thrown) {
        if (thrown instanceof RuntimeException runtimeException) {
            return runtimeException;
        }
        if (thrown instanceof Error error) {
            throw error;
        }
        return new IllegalStateException(thrown);
    }
}
