package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.RequestAttributes;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ConcurrentRequestScopeSpiTest {

    private ConcurrentRequestScope scope;

    @BeforeEach
    void setUp() {
        scope = new ConcurrentRequestScope(new ConcurrentRequestScopeSettings(10, true));
    }

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        scope.clearForTesting();
    }

    @Test
    void sameRequestResolvesSameEntryAndBean() {
        bindRequest(new MockHttpServletRequest());

        Object first = scope.get("bean", Object::new);
        Object second = scope.get("bean", Object::new);

        assertSame(first, second);
        assertNotNull(scope.getConversationId());
        assertEquals(1, scope.stateForTesting().activeEntryCount());
    }

    @Test
    void differentRequestsResolveIsolatedEntries() {
        bindRequest(new MockHttpServletRequest());
        Object first = scope.get("bean", Object::new);
        String firstConversationId = scope.getConversationId();

        bindRequest(new MockHttpServletRequest());
        Object second = scope.get("bean", Object::new);
        String secondConversationId = scope.getConversationId();

        assertNotEquals(first, second);
        assertNotEquals(firstConversationId, secondConversationId);
        assertEquals(2, scope.stateForTesting().activeEntryCount());
    }

    @Test
    void concurrentRequestsWithSameBeanNameStayIsolated() throws Exception {
        int workersPerRequest = 8;
        ServletRequestAttributes attrsA = new ServletRequestAttributes(
                new MockHttpServletRequest(), new MockHttpServletResponse());
        ServletRequestAttributes attrsB = new ServletRequestAttributes(
                new MockHttpServletRequest(), new MockHttpServletResponse());
        Set<Object> requestAInstances = ConcurrentHashMap.newKeySet();
        Set<Object> requestBInstances = ConcurrentHashMap.newKeySet();
        Set<String> requestAConversationIds = ConcurrentHashMap.newKeySet();
        Set<String> requestBConversationIds = ConcurrentHashMap.newKeySet();
        AtomicInteger requestAFactoryCalls = new AtomicInteger();
        AtomicInteger requestBFactoryCalls = new AtomicInteger();
        ConcurrentLinkedQueue<Throwable> errors = new ConcurrentLinkedQueue<>();
        CountDownLatch ready = new CountDownLatch(workersPerRequest * 2);
        CountDownLatch start = new CountDownLatch(1);
        CountDownLatch done = new CountDownLatch(workersPerRequest * 2);

        for (int i = 0; i < workersPerRequest; i++) {
            startRequestWorker(attrsA, requestAInstances, requestAConversationIds,
                    requestAFactoryCalls, ready, start, done, errors);
            startRequestWorker(attrsB, requestBInstances, requestBConversationIds,
                    requestBFactoryCalls, ready, start, done, errors);
        }

        assertTrue(ready.await(5, TimeUnit.SECONDS));
        start.countDown();
        assertTrue(done.await(10, TimeUnit.SECONDS));

        assertTrue(errors.isEmpty(), () -> errors.toString());
        assertEquals(1, requestAFactoryCalls.get());
        assertEquals(1, requestBFactoryCalls.get());
        assertEquals(1, requestAInstances.size());
        assertEquals(1, requestBInstances.size());
        assertNotEquals(requestAInstances.iterator().next(), requestBInstances.iterator().next());
        assertEquals(1, requestAConversationIds.size());
        assertEquals(1, requestBConversationIds.size());
        assertNotEquals(requestAConversationIds.iterator().next(), requestBConversationIds.iterator().next());
        assertEquals(2, scope.stateForTesting().activeEntryCount());
        assertTrue(scope.stateForTesting().capacityInvariantHolds());
    }

    @Test
    void conversationIdIsNullBeforeEntryAndStableAfterCreation() {
        bindRequest(new MockHttpServletRequest());

        assertNull(scope.getConversationId());
        scope.get("trigger", Object::new);
        String first = scope.getConversationId();
        String second = scope.getConversationId();

        assertNotNull(first);
        assertEquals(first, second);
    }

    @Test
    void conversationIdReturnsNullAfterRequestCompletionCleanup() {
        ServletRequestAttributes attrs = new ServletRequestAttributes(
                new MockHttpServletRequest(), new MockHttpServletResponse());
        RequestContextHolder.setRequestAttributes(attrs);

        scope.get("trigger", Object::new);
        assertNotNull(scope.getConversationId());

        attrs.requestCompleted();

        assertNull(scope.getConversationId());
        assertEquals(0, scope.stateForTesting().activeEntryCount());
        assertTrue(scope.stateForTesting().capacityInvariantHolds());
    }

    @Test
    void removeReturnsRemovedBeanAndAllowsFreshCreation() {
        bindRequest(new MockHttpServletRequest());
        Object original = scope.get("removable", Object::new);

        Object removed = scope.remove("removable");
        Object fresh = scope.get("removable", Object::new);

        assertSame(original, removed);
        assertNotEquals(original, fresh);
    }

    @Test
    void removeAbsentBeanReturnsNull() {
        bindRequest(new MockHttpServletRequest());

        assertNull(scope.remove("absent"));
    }

    @Test
    void removeWithoutContextReturnsNull() {
        assertNull(scope.remove("absent"));
    }

    @Test
    void registerDestructionCallbackIsModuleOwnedAfterEntryCreation() {
        RecordingRequestAttributes attrs = new RecordingRequestAttributes();
        RequestContextHolder.setRequestAttributes(attrs);
        Runnable callback = () -> { };

        scope.get("bean", Object::new);
        scope.registerDestructionCallback("bean", callback);

        assertEquals(1, attrs.callbackRegistrations);
        assertEquals(ConcurrentRequestScope.class.getName() + ".cleanup", attrs.callbackName);
        assertNotEquals(callback, attrs.callback);
        assertEquals(RequestAttributes.SCOPE_REQUEST, attrs.callbackScope);
    }

    @Test
    void registerDestructionCallbackWithContextButNoEntryThrowsIllegalStateException() {
        RequestContextHolder.setRequestAttributes(new RecordingRequestAttributes());

        assertThrows(IllegalStateException.class,
                () -> scope.registerDestructionCallback("bean", () -> { }));
    }

    @Test
    void resolveContextualObjectDelegatesToRequestAttributes() {
        RecordingRequestAttributes attrs = new RecordingRequestAttributes();
        Object contextualObject = new Object();
        attrs.references.put("custom", contextualObject);
        RequestContextHolder.setRequestAttributes(attrs);

        assertSame(contextualObject, scope.resolveContextualObject("custom"));
        assertNull(scope.resolveContextualObject("missing"));
    }

    @Test
    void resolveContextualObjectKnownRequestReferenceDelegatesToServletRequestAttributes() {
        MockHttpServletRequest request = new MockHttpServletRequest();
        bindRequest(request);

        assertSame(request, scope.resolveContextualObject(RequestAttributes.REFERENCE_REQUEST));
    }

    @Test
    void getAndResolveWithoutContextThrowIllegalStateException() {
        assertThrows(IllegalStateException.class, () -> scope.get("bean", Object::new));
        assertThrows(IllegalStateException.class, () -> scope.resolveContextualObject("request"));
        assertThrows(IllegalStateException.class,
                () -> scope.registerDestructionCallback("bean", () -> { }));
    }

    @Test
    void getConversationIdWithoutContextReturnsNull() {
        assertNull(scope.getConversationId());
    }

    @Test
    void wrappingSameServletRequestUsesSameEntry() {
        MockHttpServletRequest request = new MockHttpServletRequest();
        RequestContextHolder.setRequestAttributes(
                new ServletRequestAttributes(request, new MockHttpServletResponse()));
        Object first = scope.get("bean", Object::new);
        String firstConversationId = scope.getConversationId();

        RequestContextHolder.setRequestAttributes(
                new ServletRequestAttributes(request, new MockHttpServletResponse()));
        Object second = scope.get("bean", Object::new);
        String secondConversationId = scope.getConversationId();

        assertSame(first, second);
        assertEquals(firstConversationId, secondConversationId);
        assertEquals(1, scope.stateForTesting().activeEntryCount());
    }

    @Test
    void scopeImplementationDoesNotUseStaticRequestEntryRegistry() {
        boolean hasStaticRegistry = Arrays.stream(ConcurrentRequestScope.class.getDeclaredFields())
                .anyMatch(field -> Modifier.isStatic(field.getModifiers())
                        && ConcurrentHashMap.class.isAssignableFrom(field.getType()));

        assertFalse(hasStaticRegistry);
    }

    private static void bindRequest(MockHttpServletRequest request) {
        RequestContextHolder.setRequestAttributes(
                new ServletRequestAttributes(request, new MockHttpServletResponse()));
    }

    private void startRequestWorker(ServletRequestAttributes attrs,
            Set<Object> instances,
            Set<String> conversationIds,
            AtomicInteger factoryCalls,
            CountDownLatch ready,
            CountDownLatch start,
            CountDownLatch done,
            ConcurrentLinkedQueue<Throwable> errors) {
        Thread.ofVirtual().start(() -> {
            RequestContextHolder.setRequestAttributes(attrs);
            try {
                ready.countDown();
                assertTrue(start.await(5, TimeUnit.SECONDS));
                Object bean = scope.get("shared", () -> {
                    factoryCalls.incrementAndGet();
                    sleepBriefly();
                    return new Object();
                });
                instances.add(bean);
                conversationIds.add(scope.getConversationId());
            } catch (Throwable t) {
                errors.add(t);
            } finally {
                RequestContextHolder.resetRequestAttributes();
                done.countDown();
            }
        });
    }

    private static void sleepBriefly() {
        try {
            Thread.sleep(25);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }

    private static final class RecordingRequestAttributes implements RequestAttributes {

        private final ConcurrentHashMap<String, Object> attributes = new ConcurrentHashMap<>();
        private final ConcurrentHashMap<String, Object> references = new ConcurrentHashMap<>();
        private int callbackRegistrations;
        private String callbackName;
        private Runnable callback;
        private int callbackScope = -1;

        @Override
        public Object getAttribute(String name, int scope) {
            return attributes.get(name);
        }

        @Override
        public void setAttribute(String name, Object value, int scope) {
            attributes.put(name, value);
        }

        @Override
        public void removeAttribute(String name, int scope) {
            attributes.remove(name);
        }

        @Override
        public String[] getAttributeNames(int scope) {
            return attributes.keySet().toArray(String[]::new);
        }

        @Override
        public void registerDestructionCallback(String name, Runnable callback, int scope) {
            callbackRegistrations++;
            this.callbackName = name;
            this.callback = callback;
            this.callbackScope = scope;
        }

        @Override
        public Object resolveReference(String key) {
            return references.get(key);
        }

        @Override
        public String getSessionId() {
            return "test-session";
        }

        @Override
        public Object getSessionMutex() {
            return this;
        }
    }
}
