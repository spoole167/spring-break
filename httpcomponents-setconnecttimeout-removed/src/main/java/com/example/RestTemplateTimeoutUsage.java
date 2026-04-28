package com.example;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.web.client.RestTemplate;
import java.time.Duration;

public class RestTemplateTimeoutUsage {
    public static RestTemplate configureWithTimeout(RestTemplateBuilder builder) {
        // This method setConnectTimeout(Duration) is removed in Spring Boot 4.0
        // It was deprecated in 3.4 in favor of connectTimeout(Duration)
        return builder.setConnectTimeout(Duration.ofSeconds(5)).build();
    }
}
