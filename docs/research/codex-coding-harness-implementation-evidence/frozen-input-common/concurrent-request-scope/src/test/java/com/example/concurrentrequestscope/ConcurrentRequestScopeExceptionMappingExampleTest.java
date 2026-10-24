package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCapacityException;
import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeCleanupException;
import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeSnapshotException;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringBootConfiguration;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpStatus;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(classes = ConcurrentRequestScopeExceptionMappingExampleTest.TestApplication.class)
@AutoConfigureMockMvc
class ConcurrentRequestScopeExceptionMappingExampleTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void capacityEndpointReturns503() throws Exception {
        mockMvc.perform(get("/phase25/capacity"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.code").value("CONCURRENT_REQUEST_SCOPE_UNAVAILABLE"));
    }

    @Test
    void snapshotEndpointReturns503() throws Exception {
        mockMvc.perform(get("/phase25/snapshot"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.code").value("CONCURRENT_REQUEST_SCOPE_UNAVAILABLE"));
    }

    @Test
    void cleanupEndpointReturns503() throws Exception {
        mockMvc.perform(get("/phase25/cleanup"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.code").value("CONCURRENT_REQUEST_SCOPE_UNAVAILABLE"));
    }

    @SpringBootConfiguration
    @EnableAutoConfiguration
    @Import({
            ScopeExceptionThrowingController.class,
            ApplicationScopeExceptionHandler.class
    })
    static class TestApplication {
    }

    @RestController
    static class ScopeExceptionThrowingController {

        @GetMapping("/phase25/capacity")
        String capacity() {
            throw new ConcurrentRequestScopeCapacityException("capacity exceeded");
        }

        @GetMapping("/phase25/snapshot")
        String snapshot() {
            throw new ConcurrentRequestScopeSnapshotException("snapshot slow-path rejected");
        }

        @GetMapping("/phase25/cleanup")
        String cleanup() {
            throw new ConcurrentRequestScopeCleanupException("cleanup failed");
        }
    }

    @RestControllerAdvice
    static class ApplicationScopeExceptionHandler {

        @ExceptionHandler({
                ConcurrentRequestScopeCapacityException.class,
                ConcurrentRequestScopeSnapshotException.class,
                ConcurrentRequestScopeCleanupException.class
        })
        @ResponseStatus(HttpStatus.SERVICE_UNAVAILABLE)
        Map<String, String> handleScopeUnavailable(RuntimeException ex) {
            return Map.of(
                    "code", "CONCURRENT_REQUEST_SCOPE_UNAVAILABLE",
                    "message", ex.getMessage());
        }
    }
}
