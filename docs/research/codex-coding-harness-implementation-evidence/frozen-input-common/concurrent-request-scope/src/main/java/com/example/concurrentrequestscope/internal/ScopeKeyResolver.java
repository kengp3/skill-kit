package com.example.concurrentrequestscope.internal;

import org.springframework.web.context.request.RequestAttributes;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.Objects;

public final class ScopeKeyResolver {

    public Object scopeKey(RequestAttributes attrs) {
        Objects.requireNonNull(attrs, "request attributes must not be null");
        if (attrs instanceof ServletRequestAttributes servletRequestAttributes) {
            return servletRequestAttributes.getRequest();
        }
        return attrs;
    }

    public boolean isSnapshot(RequestAttributes attrs) {
        Objects.requireNonNull(attrs, "request attributes must not be null");
        return attrs instanceof ServletRequestAttributes
                && attrs.getClass().getSimpleName().endsWith("SnapshotServletRequestAttributes");
    }
}
