package com.example.concurrentrequestscope.exception;

public class ConcurrentRequestScopeBackdoorException extends ConcurrentRequestScopeException {

    public ConcurrentRequestScopeBackdoorException(String message) {
        super(message);
    }

    public ConcurrentRequestScopeBackdoorException(String message, Throwable cause) {
        super(message, cause);
    }
}
