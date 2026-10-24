package com.example.concurrentrequestscope.exception;

public class ConcurrentRequestScopeSnapshotException extends ConcurrentRequestScopeException {

    public ConcurrentRequestScopeSnapshotException(String message) {
        super(message);
    }

    public ConcurrentRequestScopeSnapshotException(String message, Throwable cause) {
        super(message, cause);
    }
}
