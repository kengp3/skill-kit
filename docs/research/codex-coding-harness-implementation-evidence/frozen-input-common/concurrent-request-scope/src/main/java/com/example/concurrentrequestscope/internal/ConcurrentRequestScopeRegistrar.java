package com.example.concurrentrequestscope.internal;

import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.beans.factory.support.BeanDefinitionRegistry;
import org.springframework.beans.factory.support.RootBeanDefinition;
import org.springframework.context.EnvironmentAware;
import org.springframework.context.annotation.ImportBeanDefinitionRegistrar;
import org.springframework.core.env.Environment;
import org.springframework.core.type.AnnotationMetadata;

public final class ConcurrentRequestScopeRegistrar implements ImportBeanDefinitionRegistrar, EnvironmentAware {

    static final String BEAN_NAME = "concurrentRequestScopeBeanFactoryPostProcessor";

    private Environment environment;

    @Override
    public void setEnvironment(Environment environment) {
        this.environment = environment;
    }

    @Override
    public void registerBeanDefinitions(AnnotationMetadata importingClassMetadata, BeanDefinitionRegistry registry) {
        if (registry.containsBeanDefinition(BEAN_NAME)) {
            return;
        }

        RootBeanDefinition beanDefinition = new RootBeanDefinition(ConcurrentRequestScopeBeanFactoryPostProcessor.class);
        beanDefinition.setRole(BeanDefinition.ROLE_INFRASTRUCTURE);
        beanDefinition.getConstructorArgumentValues().addIndexedArgumentValue(0, environment);
        registry.registerBeanDefinition(BEAN_NAME, beanDefinition);
    }
}
