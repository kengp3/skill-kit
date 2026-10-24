package com.example.concurrentrequestscope.support;

import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

public final class MockRequestAttributesFixtures {

    private MockRequestAttributesFixtures() {
    }

    public static ServletRequestAttributes bindRequest() {
        return bindRequest(new MockHttpServletRequest());
    }

    public static ServletRequestAttributes bindRequest(MockHttpServletRequest request) {
        ServletRequestAttributes attrs = new ServletRequestAttributes(request);
        RequestContextHolder.setRequestAttributes(attrs);
        return attrs;
    }

    public static void resetRequest() {
        RequestContextHolder.resetRequestAttributes();
    }
}
