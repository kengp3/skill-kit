package com.example.concurrentrequestscope.support;

import com.example.concurrentrequestscope.ConcurrentRequestScope;
import com.example.concurrentrequestscope.ConcurrentRequestScopeNames;
import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeSettings;
import org.springframework.beans.factory.DisposableBean;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.config.BeanFactoryPostProcessor;
import org.springframework.beans.factory.config.ConfigurableBeanFactory;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Scope;
import org.springframework.context.annotation.ScopedProxyMode;

import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

@Configuration(proxyBeanMethods = false)
public class ConcurrentRequestScopeTestConfig {

    private static final ConcurrentRequestScope TEST_SCOPE =
            new ConcurrentRequestScope(new ConcurrentRequestScopeSettings(50, true));

    @Bean
    public static BeanFactoryPostProcessor concurrentRequestScopeRegistrar() {
        return beanFactory -> ((ConfigurableBeanFactory) beanFactory).registerScope(
                ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE,
                TEST_SCOPE);
    }

    public static ConcurrentRequestScope testScope() {
        return TEST_SCOPE;
    }

    @Bean
    @Scope(value = ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE,
            proxyMode = ScopedProxyMode.TARGET_CLASS)
    public ScopedProbe scopedProbe() {
        return new ScopedProbe();
    }

    @Bean
    public ScopedProxyConsumer scopedProxyConsumer(ScopedProbe scopedProbe) {
        return new ScopedProxyConsumer(scopedProbe);
    }

    @Bean
    @Scope(ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE)
    public ProviderScopedProbe providerScopedProbe() {
        return new ProviderScopedProbe();
    }

    @Bean
    public ProviderConsumer providerConsumer(ObjectProvider<ProviderScopedProbe> provider) {
        return new ProviderConsumer(provider);
    }

    @Bean
    @Scope(ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE)
    public NestedScopedBeanB nestedScopedBeanB() {
        return new NestedScopedBeanB();
    }

    @Bean
    @Scope(ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE)
    public NestedScopedBeanA nestedScopedBeanA(NestedScopedBeanB nestedScopedBeanB) {
        return new NestedScopedBeanA(nestedScopedBeanB);
    }

    @Bean("BB")
    @Scope(ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE)
    public CollidingScopedBean collidingBeanB() {
        return new CollidingScopedBean("BB", null);
    }

    @Bean("Aa")
    @Scope(ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE)
    public CollidingScopedBean collidingBeanA(@Qualifier("BB") CollidingScopedBean beanB) {
        return new CollidingScopedBean("Aa", beanB);
    }

    @Bean
    @Scope(ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE)
    public DestroyAwareScopedBean destroyAwareScopedBean() {
        return new DestroyAwareScopedBean();
    }

    public static class ScopedProbe {

        private final String id = UUID.randomUUID().toString();

        public String id() {
            return id;
        }
    }

    public static class ScopedProxyConsumer {

        private final ScopedProbe scopedProbe;

        public ScopedProxyConsumer(ScopedProbe scopedProbe) {
            this.scopedProbe = scopedProbe;
        }

        public String scopedProbeId() {
            return scopedProbe.id();
        }
    }

    public static class ProviderScopedProbe {

        private final String id = UUID.randomUUID().toString();

        public String id() {
            return id;
        }
    }

    public static class ProviderConsumer {

        private final ObjectProvider<ProviderScopedProbe> provider;

        public ProviderConsumer(ObjectProvider<ProviderScopedProbe> provider) {
            this.provider = provider;
        }

        public String providerScopedProbeId() {
            return provider.getObject().id();
        }

        public ProviderScopedProbe providerScopedProbe() {
            return provider.getObject();
        }
    }

    public static class NestedScopedBeanA {

        private final String id = UUID.randomUUID().toString();
        private final NestedScopedBeanB beanB;

        public NestedScopedBeanA(NestedScopedBeanB beanB) {
            this.beanB = beanB;
        }

        public String id() {
            return id;
        }

        public NestedScopedBeanB beanB() {
            return beanB;
        }
    }

    public static class NestedScopedBeanB {

        private final String id = UUID.randomUUID().toString();

        public String id() {
            return id;
        }
    }

    public static class CollidingScopedBean {

        private final String name;
        private final String id = UUID.randomUUID().toString();
        private final CollidingScopedBean dependency;

        public CollidingScopedBean(String name, CollidingScopedBean dependency) {
            this.name = name;
            this.dependency = dependency;
        }

        public String name() {
            return name;
        }

        public String id() {
            return id;
        }

        public CollidingScopedBean dependency() {
            return dependency;
        }
    }

    public static class DestroyAwareScopedBean implements DisposableBean {

        private static final AtomicInteger DESTROY_COUNT = new AtomicInteger();
        private final String id = UUID.randomUUID().toString();

        public static void resetDestroyCount() {
            DESTROY_COUNT.set(0);
        }

        public static int destroyCount() {
            return DESTROY_COUNT.get();
        }

        public String id() {
            return id;
        }

        @Override
        public void destroy() {
            DESTROY_COUNT.incrementAndGet();
        }
    }
}
