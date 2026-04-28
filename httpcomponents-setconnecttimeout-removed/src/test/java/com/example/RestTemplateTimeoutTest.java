package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.web.client.RestTemplate;
import java.lang.reflect.Method;
import java.time.Duration;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/* Master list: 1.34 — RestTemplateBuilder.setConnectTimeout removed */
public class RestTemplateTimeoutTest {

    @Test
    void setConnectTimeoutMethodShouldExistOnBoot35() {
        // Direct call — fails to compile on Boot 4.0
        RestTemplate restTemplate = RestTemplateTimeoutUsage.configureWithTimeout(new RestTemplateBuilder());
        assertNotNull(restTemplate);
    }

    @Test
    void setConnectTimeoutIsDiscoverableViaReflection() {
        boolean methodExists = false;
        try {
            Method method = RestTemplateBuilder.class.getMethod("setConnectTimeout", Duration.class);
            methodExists = true;
        } catch (NoSuchMethodException e) {
            methodExists = false;
        }

        assertTrue(methodExists, "setConnectTimeout(Duration) should be available on RestTemplateBuilder in Boot 3.5");
    }
}
