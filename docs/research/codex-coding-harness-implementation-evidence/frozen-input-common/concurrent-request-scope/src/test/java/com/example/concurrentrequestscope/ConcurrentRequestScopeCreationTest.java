package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.BeanCurrentlyInCreationException;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.Collection;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.IntStream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ConcurrentRequestScopeCreationTest {

    private ConcurrentRequestScope scope;
    private ServletRequestAttributes attrs;

    @BeforeEach
    void setUp() {
        scope = new ConcurrentRequestScope(new ConcurrentRequestScopeSettings(20, true));
        attrs = new ServletRequestAttributes(new MockHttpServletRequest(), new MockHttpServletResponse());
        RequestContextHolder.setRequestAttributes(attrs);
    }

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        scope.clearForTesting();
    }

    @Test
    void sameNameConcurrentWorkersRunExactlyOneFactory() throws Exception {
        int workers = 30;
        AtomicInteger factoryCalls = new AtomicInteger();
        AtomicInteger errors = new AtomicInteger();
        Set<Object> instances = ConcurrentHashMap.newKeySet();
        CountDownLatch ready = new CountDownLatch(workers);
        CountDownLatch start = new CountDownLatch(1);
        CountDownLatch done = new CountDownLatch(workers);

        for (int i = 0; i < workers; i++) {
            Thread.ofVirtual().start(() -> {
                RequestContextHolder.setRequestAttributes(attrs);
                try {
                    ready.countDown();
                    assertTrue(start.await(5, TimeUnit.SECONDS));
                    instances.add(scope.get("shared", () -> {
                        factoryCalls.incrementAndGet();
                        sleepBriefly();
                        return new Object();
                    }));
                } catch (Throwable t) {
                    errors.incrementAndGet();
                } finally {
                    RequestContextHolder.resetRequestAttributes();
                    done.countDown();
                }
            });
        }

        assertTrue(ready.await(5, TimeUnit.SECONDS));
        start.countDown();
        assertTrue(done.await(10, TimeUnit.SECONDS));
        assertEquals(0, errors.get());
        assertEquals(1, factoryCalls.get());
        assertEquals(1, instances.size());
    }

    @Test
    void workerWaitersReceiveSameResult() {
        AtomicInteger factoryCalls = new AtomicInteger();

        Object first = scope.get("same", () -> {
            factoryCalls.incrementAndGet();
            return new Object();
        });
        Object second = scope.get("same", () -> {
            factoryCalls.incrementAndGet();
            return new Object();
        });

        assertSame(first, second);
        assertEquals(1, factoryCalls.get());
    }

    @Test
    void contendedFactoryFailureWakesWaitersAndRetrySucceeds() throws Exception {
        int waiters = 8;
        AtomicInteger factoryCalls = new AtomicInteger();
        CountDownLatch factoryEntered = new CountDownLatch(1);
        CountDownLatch releaseFactory = new CountDownLatch(1);
        CountDownLatch waitersReady = new CountDownLatch(waiters);
        CountDownLatch waitersDone = new CountDownLatch(waiters);
        CountDownLatch creatorDone = new CountDownLatch(1);
        ConcurrentLinkedQueue<Throwable> failures = new ConcurrentLinkedQueue<>();
        IllegalStateException boom = new IllegalStateException("boom");

        Thread.ofVirtual().start(() -> {
            RequestContextHolder.setRequestAttributes(attrs);
            try {
                scope.get("fragile", () -> {
                    factoryCalls.incrementAndGet();
                    factoryEntered.countDown();
                    await(releaseFactory);
                    throw boom;
                });
            } catch (Throwable t) {
                failures.add(t);
            } finally {
                RequestContextHolder.resetRequestAttributes();
                creatorDone.countDown();
            }
        });

        assertTrue(factoryEntered.await(5, TimeUnit.SECONDS));

        for (int i = 0; i < waiters; i++) {
            Thread.ofVirtual().start(() -> {
                RequestContextHolder.setRequestAttributes(attrs);
                try {
                    waitersReady.countDown();
                    scope.get("fragile", () -> {
                        factoryCalls.incrementAndGet();
                        throw new AssertionError("waiter must not execute the factory");
                    });
                } catch (Throwable t) {
                    failures.add(t);
                } finally {
                    RequestContextHolder.resetRequestAttributes();
                    waitersDone.countDown();
                }
            });
        }

        assertTrue(waitersReady.await(5, TimeUnit.SECONDS));
        sleepBriefly();
        releaseFactory.countDown();

        assertTrue(creatorDone.await(5, TimeUnit.SECONDS));
        assertTrue(waitersDone.await(5, TimeUnit.SECONDS));
        assertEquals(waiters + 1, failures.size());
        failures.forEach(failure -> assertSame(boom, failure));
        assertEquals(1, factoryCalls.get());

        Object recovered = scope.get("fragile", () -> {
            factoryCalls.incrementAndGet();
            return new Object();
        });

        assertNotNull(recovered);
        assertEquals(2, factoryCalls.get());
    }

    @Test
    void factoryFailureDoesNotPoisonStateAndCanRetry() {
        AtomicInteger factoryCalls = new AtomicInteger();

        assertThrows(IllegalStateException.class, () -> scope.get("fragile", () -> {
            factoryCalls.incrementAndGet();
            throw new IllegalStateException("boom");
        }));

        Object recovered = scope.get("fragile", () -> {
            factoryCalls.incrementAndGet();
            return new Object();
        });

        assertNotNull(recovered);
        assertEquals(2, factoryCalls.get());
    }

    @Test
    void contendedNullFactoryResultWakesWaitersAndRetrySucceeds() throws Exception {
        int waiters = 8;
        AtomicInteger factoryCalls = new AtomicInteger();
        CountDownLatch factoryEntered = new CountDownLatch(1);
        CountDownLatch releaseFactory = new CountDownLatch(1);
        CountDownLatch waitersReady = new CountDownLatch(waiters);
        CountDownLatch waitersDone = new CountDownLatch(waiters);
        CountDownLatch creatorDone = new CountDownLatch(1);
        ConcurrentLinkedQueue<Throwable> failures = new ConcurrentLinkedQueue<>();

        Thread.ofVirtual().start(() -> {
            RequestContextHolder.setRequestAttributes(attrs);
            try {
                scope.get("nullBean", () -> {
                    factoryCalls.incrementAndGet();
                    factoryEntered.countDown();
                    await(releaseFactory);
                    return null;
                });
            } catch (Throwable t) {
                failures.add(t);
            } finally {
                RequestContextHolder.resetRequestAttributes();
                creatorDone.countDown();
            }
        });

        assertTrue(factoryEntered.await(5, TimeUnit.SECONDS));

        for (int i = 0; i < waiters; i++) {
            Thread.ofVirtual().start(() -> {
                RequestContextHolder.setRequestAttributes(attrs);
                try {
                    waitersReady.countDown();
                    scope.get("nullBean", () -> {
                        factoryCalls.incrementAndGet();
                        throw new AssertionError("waiter must not execute the factory");
                    });
                } catch (Throwable t) {
                    failures.add(t);
                } finally {
                    RequestContextHolder.resetRequestAttributes();
                    waitersDone.countDown();
                }
            });
        }

        assertTrue(waitersReady.await(5, TimeUnit.SECONDS));
        sleepBriefly();
        releaseFactory.countDown();

        assertTrue(creatorDone.await(5, TimeUnit.SECONDS));
        assertTrue(waitersDone.await(5, TimeUnit.SECONDS));
        assertEquals(waiters + 1, failures.size());
        assertEquals(1, identitySet(failures).size());
        failures.forEach(failure -> {
            assertTrue(failure instanceof IllegalStateException);
            assertTrue(failure.getMessage().contains("objectFactory returned null"));
        });
        assertEquals(1, factoryCalls.get());

        Object recovered = scope.get("nullBean", () -> {
            factoryCalls.incrementAndGet();
            return new Object();
        });

        assertNotNull(recovered);
        assertEquals(2, factoryCalls.get());
    }

    @Test
    void sameRequestManyBeanNamesInitializeIndependentlyUnderFanOut() throws Exception {
        List<String> beanNames = IntStream.range(0, 12)
                .mapToObj(index -> "bean-" + index)
                .toList();
        int repeatsPerName = 4;
        int workers = beanNames.size() * repeatsPerName;
        Map<String, Object> expectedInstances = new ConcurrentHashMap<>();
        Map<String, AtomicInteger> factoryCalls = new ConcurrentHashMap<>();
        Map<String, Set<Object>> observedInstances = new ConcurrentHashMap<>();
        ConcurrentLinkedQueue<Throwable> errors = new ConcurrentLinkedQueue<>();
        CountDownLatch ready = new CountDownLatch(workers);
        CountDownLatch start = new CountDownLatch(1);
        CountDownLatch done = new CountDownLatch(workers);

        beanNames.forEach(name -> {
            expectedInstances.put(name, new Object());
            factoryCalls.put(name, new AtomicInteger());
            observedInstances.put(name, ConcurrentHashMap.newKeySet());
        });

        for (String beanName : beanNames) {
            for (int i = 0; i < repeatsPerName; i++) {
                Thread.ofVirtual().start(() -> {
                    RequestContextHolder.setRequestAttributes(attrs);
                    try {
                        ready.countDown();
                        assertTrue(start.await(5, TimeUnit.SECONDS));
                        Object bean = scope.get(beanName, () -> {
                            factoryCalls.get(beanName).incrementAndGet();
                            sleepBriefly();
                            return expectedInstances.get(beanName);
                        });
                        observedInstances.get(beanName).add(bean);
                    } catch (Throwable t) {
                        errors.add(t);
                    } finally {
                        RequestContextHolder.resetRequestAttributes();
                        done.countDown();
                    }
                });
            }
        }

        assertTrue(ready.await(5, TimeUnit.SECONDS));
        start.countDown();
        assertTrue(done.await(10, TimeUnit.SECONDS));
        assertEquals(List.of(), List.copyOf(errors));

        for (String beanName : beanNames) {
            assertEquals(1, factoryCalls.get(beanName).get(), beanName);
            assertEquals(1, observedInstances.get(beanName).size(), beanName);
            assertSame(expectedInstances.get(beanName), observedInstances.get(beanName).iterator().next(), beanName);
        }
    }

    @Test
    void nullFactoryResultIsRejectedAndCanRetry() {
        AtomicInteger factoryCalls = new AtomicInteger();

        assertThrows(IllegalStateException.class, () -> scope.get("nullBean", () -> {
            factoryCalls.incrementAndGet();
            return null;
        }));

        Object recovered = scope.get("nullBean", () -> {
            factoryCalls.incrementAndGet();
            return new Object();
        });

        assertNotNull(recovered);
        assertEquals(2, factoryCalls.get());
    }

    @Test
    void sameNameCircularCreationFailsFast() {
        BeanCurrentlyInCreationException ex = assertThrows(
                BeanCurrentlyInCreationException.class,
                () -> scope.get("cycle", () -> scope.get("cycle", Object::new)));

        assertEquals("cycle", ex.getBeanName());
        assertNotNull(scope.get("cycle", Object::new));
    }

    private static Set<Throwable> identitySet(Collection<Throwable> failures) {
        Set<Throwable> uniqueFailures = Collections.newSetFromMap(new IdentityHashMap<>());
        uniqueFailures.addAll(failures);
        return uniqueFailures;
    }

    private static void await(CountDownLatch latch) {
        try {
            assertTrue(latch.await(5, TimeUnit.SECONDS));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }

    private static void sleepBriefly() {
        try {
            Thread.sleep(25);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }
}
