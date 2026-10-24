package com.example.concurrentrequestscope.example;

import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCapacityException;
import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCleanupException;
import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeSnapshotException;
import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.MDC;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;
import java.util.function.Supplier;

@RestController
public class ConcurrentRequestScopeExampleController {

    private final ConcurrentRequestScopeExampleTaskContext taskContext;
    private final ConcurrentRequestScopeExampleService service;

    ConcurrentRequestScopeExampleController(
            ConcurrentRequestScopeExampleTaskContext taskContext,
            ConcurrentRequestScopeExampleService service) {
        this.taskContext = taskContext;
        this.service = service;
    }

    @GetMapping("/concurrent-request-scope/example/platform")
    public ConcurrentRequestScopeExampleService.ExampleWorkerResult platform(
            HttpServletRequest request,
            @RequestHeader(value = "x-request-id", required = false) String requestId) {
        return runWithRequestContext(request, requestId, service::runPlatformWorker);
    }

    @GetMapping("/concurrent-request-scope/example/virtual")
    public ConcurrentRequestScopeExampleService.ExampleWorkerResult virtual(
            HttpServletRequest request,
            @RequestHeader(value = "x-request-id", required = false) String requestId) {
        return runWithRequestContext(request, requestId, service::runVirtualWorker);
    }

    @GetMapping("/concurrent-request-scope/example/errors/capacity")
    public String capacityError() {
        throw new ConcurrentRequestScopeCapacityException("example capacity exceeded");
    }

    @GetMapping("/concurrent-request-scope/example/errors/snapshot")
    public String snapshotError() {
        throw new ConcurrentRequestScopeSnapshotException("example snapshot rejected");
    }

    @GetMapping("/concurrent-request-scope/example/errors/cleanup")
    public String cleanupError() {
        throw new ConcurrentRequestScopeCleanupException("example cleanup failed");
    }

    private ConcurrentRequestScopeExampleService.ExampleWorkerResult runWithRequestContext(
            HttpServletRequest request,
            String requestIdHeader,
            Supplier<ConcurrentRequestScopeExampleService.ExampleWorkerResult> action) {
        String requestId = requestIdHeader != null && !requestIdHeader.isBlank()
                ? requestIdHeader
                : UUID.randomUUID().toString();
        String method = request.getMethod();
        String path = request.getRequestURI();

        taskContext.init(requestId, method, path);
        MDC.put("app.requestId", requestId);
        MDC.put("app.method", method);
        MDC.put("app.path", path);
        MDC.put("app.unselected", "example-secret");
        try {
            return action.get();
        } finally {
            MDC.remove("app.requestId");
            MDC.remove("app.method");
            MDC.remove("app.path");
            MDC.remove("app.unselected");
        }
    }
}
