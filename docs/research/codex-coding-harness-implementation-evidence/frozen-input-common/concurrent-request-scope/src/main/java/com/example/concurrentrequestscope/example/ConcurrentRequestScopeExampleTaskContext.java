package com.example.concurrentrequestscope.example;

import java.util.UUID;

public class ConcurrentRequestScopeExampleTaskContext {

    private final String scopedId = UUID.randomUUID().toString();
    private volatile String requestId;
    private volatile String method;
    private volatile String path;

    public void init(String requestId, String method, String path) {
        this.requestId = requestId;
        this.method = method;
        this.path = path;
    }

    public String scopedId() {
        return scopedId;
    }

    public String requestId() {
        return requestId;
    }

    public String method() {
        return method;
    }

    public String path() {
        return path;
    }
}
