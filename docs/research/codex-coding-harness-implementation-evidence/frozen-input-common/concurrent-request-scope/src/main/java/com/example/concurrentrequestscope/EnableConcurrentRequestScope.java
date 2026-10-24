package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeRegistrar;
import org.springframework.context.annotation.Import;

import java.lang.annotation.Documented;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@Import(ConcurrentRequestScopeRegistrar.class)
public @interface EnableConcurrentRequestScope {
}
