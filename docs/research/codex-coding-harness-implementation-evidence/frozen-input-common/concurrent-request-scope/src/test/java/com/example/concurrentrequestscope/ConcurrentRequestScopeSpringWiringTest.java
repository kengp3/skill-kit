package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.support.ConcurrentRequestScopeTestConfig;
import com.example.concurrentrequestscope.support.MockRequestAttributesFixtures;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.concurrent.atomic.AtomicReference;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;

@SpringJUnitConfig(ConcurrentRequestScopeTestConfig.class)
class ConcurrentRequestScopeSpringWiringTest {

    @Autowired
    private ConcurrentRequestScopeTestConfig.ScopedProbe scopedProbe;

    @Autowired
    private ConcurrentRequestScopeTestConfig.ScopedProxyConsumer scopedProxyConsumer;

    @Autowired
    private ConcurrentRequestScopeTestConfig.ProviderConsumer providerConsumer;

    @Autowired
    private ApplicationContext applicationContext;

    @AfterEach
    void tearDown() {
        MockRequestAttributesFixtures.resetRequest();
        ConcurrentRequestScopeTestConfig.testScope().clearForTesting();
    }

    @Test
    void springRegistersConcurrentRequestScope() {
        MockRequestAttributesFixtures.bindRequest();

        assertNotNull(scopedProbe.id());
        assertEquals(1, ConcurrentRequestScopeTestConfig.testScope().stateForTesting().activeEntryCount());
    }

    @Test
    void sameRequestScopedBeanIdentityIsStableThroughSpringProxy() {
        MockRequestAttributesFixtures.bindRequest();

        String first = scopedProbe.id();
        String second = scopedProbe.id();

        assertEquals(first, second);
    }

    @Test
    void differentRequestsResolveIsolatedScopedBeanInstances() {
        MockRequestAttributesFixtures.bindRequest();
        String firstRequestId = scopedProbe.id();

        MockRequestAttributesFixtures.bindRequest();
        String secondRequestId = scopedProbe.id();

        assertNotEquals(firstRequestId, secondRequestId);
    }

    @Test
    void singletonConsumerSeesStableScopedProxyTargetWithinRequest() {
        MockRequestAttributesFixtures.bindRequest();

        String proxyId = scopedProbe.id();
        String firstConsumerRead = scopedProxyConsumer.scopedProbeId();
        String secondConsumerRead = scopedProxyConsumer.scopedProbeId();

        assertEquals(proxyId, firstConsumerRead);
        assertEquals(firstConsumerRead, secondConsumerRead);
    }

    @Test
    void singletonConsumerScopedProxyTargetIsIsolatedAcrossRequests() {
        MockRequestAttributesFixtures.bindRequest();
        String firstRequestId = scopedProxyConsumer.scopedProbeId();

        MockRequestAttributesFixtures.bindRequest();
        String secondRequestId = scopedProxyConsumer.scopedProbeId();

        assertNotEquals(firstRequestId, secondRequestId);
    }

    @Test
    void objectProviderResolvesStableScopedBeanWithinRequest() {
        MockRequestAttributesFixtures.bindRequest();

        ConcurrentRequestScopeTestConfig.ProviderScopedProbe first = providerConsumer.providerScopedProbe();
        ConcurrentRequestScopeTestConfig.ProviderScopedProbe second = providerConsumer.providerScopedProbe();

        assertSame(first, second);
        assertEquals(first.id(), providerConsumer.providerScopedProbeId());
    }

    @Test
    void objectProviderResolvesIsolatedScopedBeansAcrossRequests() {
        MockRequestAttributesFixtures.bindRequest();
        ConcurrentRequestScopeTestConfig.ProviderScopedProbe first = providerConsumer.providerScopedProbe();

        MockRequestAttributesFixtures.bindRequest();
        ConcurrentRequestScopeTestConfig.ProviderScopedProbe second = providerConsumer.providerScopedProbe();

        assertNotEquals(first.id(), second.id());
    }

    @Test
    void springManagedNestedScopedBeansAreStableWithinRequest() {
        MockRequestAttributesFixtures.bindRequest();

        ConcurrentRequestScopeTestConfig.NestedScopedBeanA first =
                applicationContext.getBean(ConcurrentRequestScopeTestConfig.NestedScopedBeanA.class);
        ConcurrentRequestScopeTestConfig.NestedScopedBeanA second =
                applicationContext.getBean(ConcurrentRequestScopeTestConfig.NestedScopedBeanA.class);

        assertSame(first, second);
        assertSame(first.beanB(), second.beanB());
        assertNotEquals(first.id(), first.beanB().id());
    }

    @Test
    void springManagedCollidingBeanNamesSupportNestedCreation() {
        assertEquals("Aa".hashCode(), "BB".hashCode());
        MockRequestAttributesFixtures.bindRequest();

        ConcurrentRequestScopeTestConfig.CollidingScopedBean beanA =
                applicationContext.getBean("Aa", ConcurrentRequestScopeTestConfig.CollidingScopedBean.class);
        ConcurrentRequestScopeTestConfig.CollidingScopedBean beanB =
                applicationContext.getBean("BB", ConcurrentRequestScopeTestConfig.CollidingScopedBean.class);

        assertEquals("Aa", beanA.name());
        assertEquals("BB", beanB.name());
        assertSame(beanB, beanA.dependency());
        assertSame(beanA, applicationContext.getBean("Aa", ConcurrentRequestScopeTestConfig.CollidingScopedBean.class));
        assertSame(beanB, applicationContext.getBean("BB", ConcurrentRequestScopeTestConfig.CollidingScopedBean.class));
        assertNotEquals(beanA.id(), beanB.id());
    }

    @Test
    void springManagedDisposableBeanRunsOnRequestCompletion() {
        ConcurrentRequestScopeTestConfig.DestroyAwareScopedBean.resetDestroyCount();
        ServletRequestAttributes attrs = MockRequestAttributesFixtures.bindRequest();

        ConcurrentRequestScopeTestConfig.DestroyAwareScopedBean bean =
                applicationContext.getBean(ConcurrentRequestScopeTestConfig.DestroyAwareScopedBean.class);
        assertNotNull(bean.id());
        assertEquals(0, ConcurrentRequestScopeTestConfig.DestroyAwareScopedBean.destroyCount());

        attrs.requestCompleted();

        assertEquals(1, ConcurrentRequestScopeTestConfig.DestroyAwareScopedBean.destroyCount());
        assertEquals(0, ConcurrentRequestScopeTestConfig.testScope().stateForTesting().activeEntryCount());
    }

    @Test
    void singletonScopedProxyWorkerMissingContextSurfacesException() throws Exception {
        MockRequestAttributesFixtures.bindRequest();
        assertNotNull(scopedProxyConsumer.scopedProbeId());
        AtomicReference<Throwable> captured = new AtomicReference<>();

        Thread worker = Thread.ofVirtual().start(() -> {
            try {
                scopedProxyConsumer.scopedProbeId();
            } catch (Throwable throwable) {
                captured.set(throwable);
            }
        });
        worker.join(5_000);

        assertFalse(worker.isAlive());
        assertNotNull(captured.get());
        assertEquals(IllegalStateException.class, rootCause(captured.get()).getClass());
    }

    private static Throwable rootCause(Throwable throwable) {
        Throwable current = throwable;
        while (current.getCause() != null) {
            current = current.getCause();
        }
        return current;
    }
}
