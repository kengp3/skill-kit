package com.example.concurrentrequestscope.example;

import com.example.concurrentrequestscope.ConcurrentRequestScopeNames;
import com.example.concurrentrequestscope.EnableConcurrentRequestScope;
import io.micrometer.context.ContextRegistry;
import io.micrometer.context.integration.Slf4jThreadLocalAccessor;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Scope;
import org.springframework.context.annotation.ScopedProxyMode;
import org.springframework.core.task.SimpleAsyncTaskExecutor;
import org.springframework.core.task.support.ContextPropagatingTaskDecorator;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;

@Configuration(proxyBeanMethods = false)
@EnableConcurrentRequestScope
public class ConcurrentRequestScopeExampleConfiguration implements InitializingBean {

    public static final String REQUEST_AWARE_EXECUTOR_BEAN =
            "concurrentRequestScopeExampleRequestAwareExecutor";

    public static final String VIRTUAL_REQUEST_AWARE_EXECUTOR_BEAN =
            "concurrentRequestScopeExampleVirtualRequestAwareExecutor";

    @Override
    public void afterPropertiesSet() {
        ContextRegistry registry = ContextRegistry.getInstance();
        boolean alreadyRegistered = registry.getThreadLocalAccessors().stream()
                .anyMatch(accessor -> Slf4jThreadLocalAccessor.KEY.equals(accessor.key()));
        if (!alreadyRegistered) {
            registry.registerThreadLocalAccessor(
                    new Slf4jThreadLocalAccessor("app.requestId", "app.method", "app.path"));
        }
    }

    @Bean(REQUEST_AWARE_EXECUTOR_BEAN)
    Executor concurrentRequestScopeExampleRequestAwareExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(4);
        executor.setQueueCapacity(20);
        executor.setThreadNamePrefix("CrsExampleReqAware-");
        executor.setTaskDecorator(new ContextPropagatingTaskDecorator());
        executor.initialize();
        return executor;
    }

    @Bean(VIRTUAL_REQUEST_AWARE_EXECUTOR_BEAN)
    Executor concurrentRequestScopeExampleVirtualRequestAwareExecutor() {
        SimpleAsyncTaskExecutor executor = new SimpleAsyncTaskExecutor("CrsExampleVirtualReq-");
        executor.setVirtualThreads(true);
        executor.setTaskDecorator(new ContextPropagatingTaskDecorator());
        return executor;
    }

    @Bean
    @Scope(value = ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE, proxyMode = ScopedProxyMode.TARGET_CLASS)
    ConcurrentRequestScopeExampleTaskContext concurrentRequestScopeExampleTaskContext() {
        return new ConcurrentRequestScopeExampleTaskContext();
    }

    @Bean
    ConcurrentRequestScopeExampleService concurrentRequestScopeExampleService(
            ConcurrentRequestScopeExampleTaskContext taskContext,
            @Qualifier(REQUEST_AWARE_EXECUTOR_BEAN) Executor requestAwareExecutor,
            @Qualifier(VIRTUAL_REQUEST_AWARE_EXECUTOR_BEAN) Executor virtualRequestAwareExecutor) {
        return new ConcurrentRequestScopeExampleService(taskContext, requestAwareExecutor, virtualRequestAwareExecutor);
    }

    @Bean
    ConcurrentRequestScopeExampleController concurrentRequestScopeExampleController(
            ConcurrentRequestScopeExampleTaskContext taskContext,
            ConcurrentRequestScopeExampleService service) {
        return new ConcurrentRequestScopeExampleController(taskContext, service);
    }

    @Bean
    ConcurrentRequestScopeExampleExceptionHandler concurrentRequestScopeExampleExceptionHandler() {
        return new ConcurrentRequestScopeExampleExceptionHandler();
    }
}
