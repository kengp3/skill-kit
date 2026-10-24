package com.example.concurrentrequestscope.example;

import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCapacityException;
import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCleanupException;
import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeSnapshotException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ConcurrentRequestScopeExampleExceptionHandler {

    @ExceptionHandler({
            ConcurrentRequestScopeCapacityException.class,
            ConcurrentRequestScopeSnapshotException.class,
            ConcurrentRequestScopeCleanupException.class
    })
    @ResponseStatus(HttpStatus.SERVICE_UNAVAILABLE)
    public ExampleErrorResponse handleScopeUnavailable(RuntimeException ex) {
        return new ExampleErrorResponse("CONCURRENT_REQUEST_SCOPE_UNAVAILABLE", ex.getMessage());
    }

    public record ExampleErrorResponse(String code, String message) {
    }
}
