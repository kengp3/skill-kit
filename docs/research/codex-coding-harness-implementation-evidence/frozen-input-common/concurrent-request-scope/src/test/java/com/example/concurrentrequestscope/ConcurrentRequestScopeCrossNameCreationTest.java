package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;

class ConcurrentRequestScopeCrossNameCreationTest {

    private ConcurrentRequestScope scope;

    @BeforeEach
    void setUp() {
        scope = new ConcurrentRequestScope(new ConcurrentRequestScopeSettings(10, true));
        RequestContextHolder.setRequestAttributes(new ServletRequestAttributes(
                new MockHttpServletRequest(),
                new MockHttpServletResponse()));
    }

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        scope.clearForTesting();
    }

    @Test
    void crossNameNestedCreationWorksForCollidingBeanNames() {
        assertEquals("Aa".hashCode(), "BB".hashCode());

        Object beanA = new Object();
        Object beanB = new Object();
        AtomicInteger beanACalls = new AtomicInteger();
        AtomicInteger beanBCalls = new AtomicInteger();

        Object createdA = assertDoesNotThrow(() -> scope.get("Aa", () -> {
            beanACalls.incrementAndGet();
            Object nestedB = scope.get("BB", () -> {
                beanBCalls.incrementAndGet();
                return beanB;
            });
            assertSame(beanB, nestedB);
            return beanA;
        }));

        assertSame(beanA, createdA);
        assertSame(beanA, scope.get("Aa", Object::new));
        assertSame(beanB, scope.get("BB", Object::new));
        assertNotSame(beanA, beanB);
        assertEquals(1, beanACalls.get());
        assertEquals(1, beanBCalls.get());
    }

    @Test
    void reverseCrossNameNestedCreationWorksForCollidingBeanNames() {
        assertEquals("Aa".hashCode(), "BB".hashCode());

        Object beanA = new Object();
        Object beanB = new Object();
        AtomicInteger beanACalls = new AtomicInteger();
        AtomicInteger beanBCalls = new AtomicInteger();

        Object createdB = assertDoesNotThrow(() -> scope.get("BB", () -> {
            beanBCalls.incrementAndGet();
            Object nestedA = scope.get("Aa", () -> {
                beanACalls.incrementAndGet();
                return beanA;
            });
            assertSame(beanA, nestedA);
            return beanB;
        }));

        assertSame(beanB, createdB);
        assertSame(beanA, scope.get("Aa", Object::new));
        assertSame(beanB, scope.get("BB", Object::new));
        assertNotSame(beanA, beanB);
        assertEquals(1, beanACalls.get());
        assertEquals(1, beanBCalls.get());
    }
}
