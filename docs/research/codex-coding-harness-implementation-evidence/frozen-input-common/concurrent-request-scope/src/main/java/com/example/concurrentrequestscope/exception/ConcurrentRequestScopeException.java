package com.example.concurrentrequestscope.exception;

public class ConcurrentRequestScopeException extends RuntimeException {

    public ConcurrentRequestScopeException(String message) {
        super(message);
    }

    public ConcurrentRequestScopeException(String message, Throwable cause) {
        super(message, cause);
    }
}
