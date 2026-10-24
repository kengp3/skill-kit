package com.example.concurrentrequestscope.support;

import com.example.concurrentrequestscope.ConcurrentRequestScopeNames;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Scope;
import org.springframework.context.annotation.ScopedProxyMode;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantLock;

@Configuration(proxyBeanMethods = false)
public class MutableBeanGuidanceConfig {

    @Bean
    @Scope(value = ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE,
            proxyMode = ScopedProxyMode.TARGET_CLASS)
    public AtomicCounterScopedBean atomicCounterScopedBean() {
        return new AtomicCounterScopedBean();
    }

    @Bean
    @Scope(value = ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE,
            proxyMode = ScopedProxyMode.TARGET_CLASS)
    public ConcurrentQueueScopedBean concurrentQueueScopedBean() {
        return new ConcurrentQueueScopedBean();
    }

    @Bean
    @Scope(value = ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE,
            proxyMode = ScopedProxyMode.TARGET_CLASS)
    public LockedAccumulatorScopedBean lockedAccumulatorScopedBean() {
        return new LockedAccumulatorScopedBean();
    }

    @Bean
    @Scope(value = ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE,
            proxyMode = ScopedProxyMode.TARGET_CLASS)
    public DeferredWriteScopedBean deferredWriteScopedBean() {
        return new DeferredWriteScopedBean();
    }

    @Bean
    @Scope(value = ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE,
            proxyMode = ScopedProxyMode.TARGET_CLASS)
    public UnsafeOverlapScopedBean unsafeOverlapScopedBean() {
        return new UnsafeOverlapScopedBean();
    }

    public static class AtomicCounterScopedBean {

        private final String id = UUID.randomUUID().toString();
        private final AtomicInteger count = new AtomicInteger();

        public String id() {
            return id;
        }

        public int increment() {
            return count.incrementAndGet();
        }

        public int count() {
            return count.get();
        }
    }

    public static class ConcurrentQueueScopedBean {

        private final String id = UUID.randomUUID().toString();
        private final ConcurrentLinkedQueue<Integer> values = new ConcurrentLinkedQueue<>();

        public String id() {
            return id;
        }

        public void add(int value) {
            values.add(value);
        }

        public List<Integer> snapshot() {
            return List.copyOf(values);
        }
    }

    public static class LockedAccumulatorScopedBean {

        private final String id = UUID.randomUUID().toString();
        private final ReentrantLock lock = new ReentrantLock();
        private int sum;

        public String id() {
            return id;
        }

        public void add(int value) {
            lock.lock();
            try {
                sum += value;
            } finally {
                lock.unlock();
            }
        }

        public int sum() {
            lock.lock();
            try {
                return sum;
            } finally {
                lock.unlock();
            }
        }
    }

    public static class DeferredWriteScopedBean {

        private final String id = UUID.randomUUID().toString();
        private final List<Integer> values = new ArrayList<>();

        public String id() {
            return id;
        }

        public void recordAfterWorkersJoin(List<Integer> workerResults) {
            values.addAll(workerResults);
        }

        public List<Integer> values() {
            return List.copyOf(values);
        }
    }

    public static class UnsafeOverlapScopedBean {

        private final String id = UUID.randomUUID().toString();
        private final AtomicInteger activeCalls = new AtomicInteger();
        private final AtomicInteger maxConcurrentCalls = new AtomicInteger();

        public String id() {
            return id;
        }

        public void enterUnsynchronizedMethod(CountDownLatch entered, CountDownLatch release) {
            int active = activeCalls.incrementAndGet();
            maxConcurrentCalls.accumulateAndGet(active, Math::max);
            entered.countDown();
            try {
                if (!release.await(5, TimeUnit.SECONDS)) {
                    throw new IllegalStateException("timed out waiting for release");
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new IllegalStateException(e);
            } finally {
                activeCalls.decrementAndGet();
            }
        }

        public int maxConcurrentCalls() {
            return maxConcurrentCalls.get();
        }
    }
}
