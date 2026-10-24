package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCapacityException;
import io.micrometer.context.ContextRegistry;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.config.BeanFactoryPostProcessor;
import org.springframework.beans.factory.config.ConfigurableBeanFactory;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.boot.test.context.runner.ApplicationContextRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ScopedProxyMode;
import org.springframework.context.support.SimpleThreadScope;
import org.springframework.core.Ordered;
import org.springframework.core.PriorityOrdered;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.web.context.request.RequestAttributesThreadLocalAccessor;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class ConcurrentRequestScopeEnablementTest {

    private final ApplicationContextRunner contextRunner = new ApplicationContextRunner()
            .withUserConfiguration(EnabledConfig.class);

    @BeforeEach
    void setUp() {
        RequestContextHolder.resetRequestAttributes();
        removeRequestAttributesAccessor();
    }

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        removeRequestAttributesAccessor();
    }

    @Test
    void enableAnnotationRegistersScopeAndScopedBeanResolvesInRequest() {
        contextRunner
                .withPropertyValues("concurrent-request-scope.testing.clear-enabled=true")
                .run(context -> {
                    ConfigurableBeanFactory beanFactory = context.getSourceApplicationContext().getBeanFactory();
                    org.springframework.beans.factory.config.Scope registeredScope =
                            beanFactory.getRegisteredScope(ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE);

                    assertThat(registeredScope).isInstanceOf(ConcurrentRequestScope.class);

                    ServletRequestAttributes requestAttributes =
                            new ServletRequestAttributes(new MockHttpServletRequest());
                    RequestContextHolder.setRequestAttributes(requestAttributes);

                    ScopedProbe probe = context.getBean(ScopedProbe.class);
                    assertThat(probe.id()).isEqualTo(probe.id());

                    ((ConcurrentRequestScope) registeredScope).clearForTesting();
                    requestAttributes.requestCompleted();
                });
    }

    @Test
    void maxActiveRequestsPropertyLimitsActiveScopeEntries() {
        contextRunner
                .withPropertyValues(
                        "concurrent-request-scope.max-active-requests=3",
                        "concurrent-request-scope.testing.clear-enabled=true")
                .run(context -> {
                    ConcurrentRequestScope scope = registeredConcurrentRequestScope(context.getSourceApplicationContext()
                            .getBeanFactory());

                    createScopedObject(scope, new MockHttpServletRequest());
                    createScopedObject(scope, new MockHttpServletRequest());
                    createScopedObject(scope, new MockHttpServletRequest());

                    assertThatThrownBy(() -> createScopedObject(scope, new MockHttpServletRequest()))
                            .isInstanceOf(ConcurrentRequestScopeCapacityException.class);

                    scope.clearForTesting();
                });
    }

    @Test
    void duplicateScopeRegistrationFailsFast() {
        new ApplicationContextRunner()
                .withUserConfiguration(DuplicateScopeConfig.class, EnabledConfig.class)
                .run(context -> {
                    assertThat(context).hasFailed();
                    assertThat(context.getStartupFailure())
                            .hasMessageContaining("ConcurrentRequestScope already registered")
                            .hasMessageContaining(ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE);
                });
    }

    @Test
    void repeatedEnablementRegistersOneRequestAttributesAccessor() {
        contextRunner.run(context -> assertThat(countRequestAttributesAccessors()).isEqualTo(1));
        contextRunner.run(context -> assertThat(countRequestAttributesAccessors()).isEqualTo(1));
    }

    private static void createScopedObject(ConcurrentRequestScope scope, MockHttpServletRequest request) {
        ServletRequestAttributes requestAttributes = new ServletRequestAttributes(request);
        RequestContextHolder.setRequestAttributes(requestAttributes);
        scope.get("probe-" + UUID.randomUUID(), Object::new);
    }

    private static ConcurrentRequestScope registeredConcurrentRequestScope(ConfigurableListableBeanFactory beanFactory) {
        return (ConcurrentRequestScope) beanFactory.getRegisteredScope(
                ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE);
    }

    private static long countRequestAttributesAccessors() {
        return ContextRegistry.getInstance().getThreadLocalAccessors().stream()
                .filter(accessor -> accessor instanceof RequestAttributesThreadLocalAccessor)
                .count();
    }

    private static void removeRequestAttributesAccessor() {
        ContextRegistry.getInstance().removeThreadLocalAccessor(RequestAttributesThreadLocalAccessor.KEY);
    }

    @Configuration(proxyBeanMethods = false)
    @EnableConcurrentRequestScope
    static class EnabledConfig {

        @Bean
        @org.springframework.context.annotation.Scope(
                value = ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE,
                proxyMode = ScopedProxyMode.TARGET_CLASS)
        ScopedProbe scopedProbe() {
            return new ScopedProbe();
        }
    }

    @Configuration(proxyBeanMethods = false)
    static class DuplicateScopeConfig {

        @Bean
        static BeanFactoryPostProcessor duplicateConcurrentRequestScopeRegistrar() {
            return new DuplicateScopePostProcessor();
        }
    }

    static final class DuplicateScopePostProcessor implements BeanFactoryPostProcessor, PriorityOrdered {

        @Override
        public int getOrder() {
            return Ordered.HIGHEST_PRECEDENCE;
        }

        @Override
        public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) {
            beanFactory.registerScope(
                    ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE,
                    new SimpleThreadScope());
        }
    }

    static class ScopedProbe {

        private final String id = UUID.randomUUID().toString();

        String id() {
            return id;
        }
    }
}
