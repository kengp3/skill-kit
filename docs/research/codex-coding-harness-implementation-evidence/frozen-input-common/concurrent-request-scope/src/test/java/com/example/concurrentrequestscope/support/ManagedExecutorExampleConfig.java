package com.example.concurrentrequestscope.support;

import com.example.concurrentrequestscope.ConcurrentRequestScopeNames;
import com.example.concurrentrequestscope.EnableConcurrentRequestScope;
import io.micrometer.context.ContextRegistry;
import io.micrometer.context.integration.Slf4jThreadLocalAccessor;
import jakarta.annotation.PostConstruct;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Scope;
import org.springframework.context.annotation.ScopedProxyMode;
import org.springframework.core.task.SimpleAsyncTaskExecutor;
import org.springframework.core.task.support.ContextPropagatingTaskDecorator;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.UUID;
import java.util.concurrent.Executor;

@Configuration(proxyBeanMethods = false)
@EnableConcurrentRequestScope
public class ManagedExecutorExampleConfig {

    @PostConstruct
    void registerSelectedMdcAccessor() {
        ContextRegistry registry = ContextRegistry.getInstance();
        boolean alreadyRegistered = registry.getThreadLocalAccessors().stream()
                .anyMatch(accessor -> Slf4jThreadLocalAccessor.KEY.equals(accessor.key()));
        if (!alreadyRegistered) {
            registry.registerThreadLocalAccessor(
                    new Slf4jThreadLocalAccessor("app.requestId", "app.method", "app.path"));
        }
    }

    @Bean("requestAwareExecutor")
    Executor requestAwareExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(4);
        executor.setQueueCapacity(20);
        executor.setThreadNamePrefix("CrsReqAware-");
        executor.setTaskDecorator(new ContextPropagatingTaskDecorator());
        executor.initialize();
        return executor;
    }

    @Bean("virtualRequestAwareExecutor")
    Executor virtualRequestAwareExecutor() {
        SimpleAsyncTaskExecutor executor = new SimpleAsyncTaskExecutor("CrsVirtualReq-");
        executor.setVirtualThreads(true);
        executor.setTaskDecorator(new ContextPropagatingTaskDecorator());
        return executor;
    }

    @Bean
    @Scope(value = ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE, proxyMode = ScopedProxyMode.TARGET_CLASS)
    ManagedExecutorScopedProbe managedExecutorScopedProbe() {
        return new ManagedExecutorScopedProbe();
    }

    public static class ManagedExecutorScopedProbe {

        private final String id = UUID.randomUUID().toString();

        public String id() {
            return id;
        }
    }
}
