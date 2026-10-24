package com.example.concurrentrequestscope.example;

import org.slf4j.MDC;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class ConcurrentRequestScopeExampleService {

    private final ConcurrentRequestScopeExampleTaskContext taskContext;
    private final Executor requestAwareExecutor;
    private final Executor virtualRequestAwareExecutor;

    ConcurrentRequestScopeExampleService(
            ConcurrentRequestScopeExampleTaskContext taskContext,
            Executor requestAwareExecutor,
            Executor virtualRequestAwareExecutor) {
        this.taskContext = taskContext;
        this.requestAwareExecutor = requestAwareExecutor;
        this.virtualRequestAwareExecutor = virtualRequestAwareExecutor;
    }

    public ExampleWorkerResult runPlatformWorker() {
        return runWorker("platform", requestAwareExecutor);
    }

    public ExampleWorkerResult runVirtualWorker() {
        return runWorker("virtual", virtualRequestAwareExecutor);
    }

    private ExampleWorkerResult runWorker(String mode, Executor executor) {
        String requestThreadScopedId = taskContext.scopedId();
        try {
            ExampleWorkerResult workerResult = CompletableFuture.supplyAsync(() -> new ExampleWorkerResult(
                            mode,
                            requestThreadScopedId,
                            taskContext.scopedId(),
                            taskContext.requestId(),
                            taskContext.method(),
                            taskContext.path(),
                            MDC.get("app.requestId"),
                            MDC.get("app.method"),
                            MDC.get("app.path"),
                            MDC.get("app.unselected"),
                            Thread.currentThread().isVirtual()), executor)
                    .get(5, TimeUnit.SECONDS);
            return workerResult;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("interrupted while running concurrent request scope example", e);
        } catch (ExecutionException | TimeoutException e) {
            throw new IllegalStateException("failed to run concurrent request scope example", e);
        }
    }

    public record ExampleWorkerResult(
            String mode,
            String requestThreadScopedId,
            String workerThreadScopedId,
            String taskContextRequestId,
            String taskContextMethod,
            String taskContextPath,
            String mdcRequestId,
            String mdcMethod,
            String mdcPath,
            String unselectedMdc,
            boolean virtualThread) {
    }
}
