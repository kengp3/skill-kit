package com.example.concurrentrequestscope;

import com.example.concurrentrequestscope.example.ConcurrentRequestScopeExampleConfiguration;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.micrometer.context.ContextRegistry;
import io.micrometer.context.integration.Slf4jThreadLocalAccessor;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.boot.SpringBootConfiguration;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.web.context.request.RequestContextHolder;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(classes = ConcurrentRequestScopeFormalExampleIntegrationTest.TestApplication.class)
@AutoConfigureMockMvc
@TestPropertySource(properties = "concurrent-request-scope.testing.clear-enabled=true")
class ConcurrentRequestScopeFormalExampleIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private ConfigurableListableBeanFactory beanFactory;

    @AfterEach
    void tearDown() {
        RequestContextHolder.resetRequestAttributes();
        MDC.clear();
        registeredScope().clearForTesting();
    }

    @AfterAll
    static void removeMdcAccessor() {
        ContextRegistry.getInstance().removeThreadLocalAccessor(Slf4jThreadLocalAccessor.KEY);
    }

    @Test
    void formalPlatformExamplePropagatesRequestContextAndSelectedMdc() throws Exception {
        MvcResult result = mockMvc.perform(get("/concurrent-request-scope/example/platform")
                        .header("x-request-id", "req-formal-platform"))
                .andExpect(status().isOk())
                .andReturn();

        JsonNode body = objectMapper.readTree(result.getResponse().getContentAsString());

        assertThat(body.path("mode").asText()).isEqualTo("platform");
        assertThat(body.path("workerThreadScopedId").asText())
                .isEqualTo(body.path("requestThreadScopedId").asText());
        assertThat(body.path("taskContextRequestId").asText()).isEqualTo("req-formal-platform");
        assertThat(body.path("taskContextMethod").asText()).isEqualTo("GET");
        assertThat(body.path("taskContextPath").asText())
                .isEqualTo("/concurrent-request-scope/example/platform");
        assertThat(body.path("mdcRequestId").asText()).isEqualTo("req-formal-platform");
        assertThat(body.path("mdcMethod").asText()).isEqualTo("GET");
        assertThat(body.path("mdcPath").asText())
                .isEqualTo("/concurrent-request-scope/example/platform");
        assertThat(body.path("unselectedMdc").isNull()).isTrue();
        assertThat(body.path("virtualThread").asBoolean()).isFalse();
    }

    @Test
    void formalVirtualExamplePropagatesRequestContextAndSelectedMdc() throws Exception {
        MvcResult result = mockMvc.perform(get("/concurrent-request-scope/example/virtual")
                        .header("x-request-id", "req-formal-virtual"))
                .andExpect(status().isOk())
                .andReturn();

        JsonNode body = objectMapper.readTree(result.getResponse().getContentAsString());

        assertThat(body.path("mode").asText()).isEqualTo("virtual");
        assertThat(body.path("workerThreadScopedId").asText())
                .isEqualTo(body.path("requestThreadScopedId").asText());
        assertThat(body.path("taskContextRequestId").asText()).isEqualTo("req-formal-virtual");
        assertThat(body.path("taskContextMethod").asText()).isEqualTo("GET");
        assertThat(body.path("taskContextPath").asText())
                .isEqualTo("/concurrent-request-scope/example/virtual");
        assertThat(body.path("mdcRequestId").asText()).isEqualTo("req-formal-virtual");
        assertThat(body.path("mdcMethod").asText()).isEqualTo("GET");
        assertThat(body.path("mdcPath").asText())
                .isEqualTo("/concurrent-request-scope/example/virtual");
        assertThat(body.path("unselectedMdc").isNull()).isTrue();
        assertThat(body.path("virtualThread").asBoolean()).isTrue();
    }

    @Test
    void formalExceptionHandlerMapsScopeExceptionsTo503() throws Exception {
        mockMvc.perform(get("/concurrent-request-scope/example/errors/capacity"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.code").value("CONCURRENT_REQUEST_SCOPE_UNAVAILABLE"));

        mockMvc.perform(get("/concurrent-request-scope/example/errors/snapshot"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.code").value("CONCURRENT_REQUEST_SCOPE_UNAVAILABLE"));

        mockMvc.perform(get("/concurrent-request-scope/example/errors/cleanup"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.code").value("CONCURRENT_REQUEST_SCOPE_UNAVAILABLE"));
    }

    private ConcurrentRequestScope registeredScope() {
        return (ConcurrentRequestScope) beanFactory.getRegisteredScope(
                ConcurrentRequestScopeNames.CONCURRENT_REQUEST_SCOPE);
    }

    @SpringBootConfiguration
    @EnableAutoConfiguration
    @Import(ConcurrentRequestScopeExampleConfiguration.class)
    static class TestApplication {
    }
}
