package com.example.concurrentrequestscope.internal;

import com.example.concurrentrequestscope.ConcurrentRequestScope;
import com.example.concurrentrequestscope.ConcurrentRequestScopeNames;
import com.example.concurrentrequestscope.ConcurrentRequestScopeProperties;
import io.micrometer.context.ContextRegistry;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.BeanCreationException;
import org.springframework.beans.factory.config.BeanFactoryPostProcessor;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.boot.context.properties.bind.Binder;
import org.springframework.core.env.Environment;
import org.springframework.web.context.request.RequestAttributesThreadLocalAccessor;

import java.util.Objects;

public final class ConcurrentRequestScopeBeanFactoryPostProcessor implements BeanFactoryPostProcessor {

    private final Environment environment;

    public ConcurrentRequestScopeBeanFactoryPostProcessor(Environment environment) {
        this.environment = Objects.requireNonNull(environment, "environment must not be null");
    }

    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException {
        registerRequestAttributesThreadLocalAccessor();

        if (beanFactory.getRegisteredScope(ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE) != null) {
            throw new BeanCreationException(
                    "ConcurrentRequestScope already registered for scope name '"
                            + ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE + "'");
        }

        ConcurrentRequestScopeProperties properties = Binder.get(environment)
                .bind("concurrent-request-scope", ConcurrentRequestScopeProperties.class)
                .orElseGet(ConcurrentRequestScopeProperties::new);

        beanFactory.registerScope(
                ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE,
                new ConcurrentRequestScope(properties.toSettings()));
    }

    private static void registerRequestAttributesThreadLocalAccessor() {
        ContextRegistry registry = ContextRegistry.getInstance();
        boolean alreadyRegistered = registry.getThreadLocalAccessors().stream()
                .anyMatch(accessor -> accessor instanceof RequestAttributesThreadLocalAccessor);
        if (!alreadyRegistered) {
            registry.registerThreadLocalAccessor(new RequestAttributesThreadLocalAccessor());
        }
    }
}
