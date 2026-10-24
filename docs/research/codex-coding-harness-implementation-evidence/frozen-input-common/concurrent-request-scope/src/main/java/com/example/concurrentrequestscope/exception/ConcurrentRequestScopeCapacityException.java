package com.example.concurrentrequestscope.exception;

public class ConcurrentRequestScopeCapacityException extends ConcurrentRequestScopeException {

    public ConcurrentRequestScopeCapacityException(String message) {
        super(message);
    }

    public ConcurrentRequestScopeCapacityException(String message, Throwable cause) {
        super(message, cause);
    }
}
