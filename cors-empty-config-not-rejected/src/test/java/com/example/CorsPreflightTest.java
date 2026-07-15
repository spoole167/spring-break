package com.example;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.options;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/* Master list: 2.17 — CORS empty config not rejected */
/* MockMvc is built manually rather than via @AutoConfigureMockMvc: that
   annotation's package relocates in Boot 4.0, which would turn this test
   into a compile-failure demo instead of exercising the CORS behaviour. */
@SpringBootTest
public class CorsPreflightTest {

    @Autowired
    private WebApplicationContext context;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.webAppContextSetup(context).build();
    }

    @Test
    void preflightWithEmptyConfigShouldBeRejectedOnBoot35() throws Exception {
        // In Spring 3.5, an empty CorsConfiguration (no allowed origins, etc) 
        // results in a 403 Forbidden for pre-flight requests.
        // In Spring 4.0, there is a behavior change where it might not be rejected
        // in the same way or headers might differ.
        
        mockMvc.perform(options("/hello")
                .header("Origin", "https://example.com")
                .header("Access-Control-Request-Method", "GET"))
                .andExpect(status().isForbidden());
    }
}
