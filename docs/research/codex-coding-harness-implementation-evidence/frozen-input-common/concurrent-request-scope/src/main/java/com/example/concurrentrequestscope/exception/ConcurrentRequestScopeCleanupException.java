package com.example.concurrentrequestscope.exception;

public class ConcurrentRequestScopeCleanupException extends ConcurrentRequestScopeException {

    public ConcurrentRequestScopeCleanupException(String message) {
        super(message);
    }

    public ConcurrentRequestScopeCleanupException(String message, Throwable cause) {
        super(message, cause);
    }
}
