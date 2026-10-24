package com.example.concurrentrequestscope.internal;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.BiConsumer;

public final class DestructionCallbackRegistry {

    private final ConcurrentHashMap<String, Runnable> callbacks = new ConcurrentHashMap<>();

    public void register(String name, Runnable callback) {
        Objects.requireNonNull(name, "bean name must not be null");
        Objects.requireNonNull(callback, "destruction callback must not be null");
        callbacks.put(name, callback);
    }

    public void remove(String name) {
        Objects.requireNonNull(name, "bean name must not be null");
        callbacks.remove(name);
    }

    public int runBestEffort(BiConsumer<String, Throwable> failureHandler) {
        Objects.requireNonNull(failureHandler, "failureHandler must not be null");
        ArrayList<Map.Entry<String, Runnable>> snapshot = new ArrayList<>(callbacks.entrySet());
        snapshot.sort(Comparator.comparing(Map.Entry::getKey));
        callbacks.clear();

        int failures = 0;
        for (Map.Entry<String, Runnable> entry : snapshot) {
            try {
                entry.getValue().run();
            } catch (Throwable thrown) {
                failures++;
                failureHandler.accept(entry.getKey(), thrown);
            }
        }
        return failures;
    }
}
