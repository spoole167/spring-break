package com.example;

import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;

/**
 * Uses the int-based timeout setters on HttpComponentsClientHttpRequestFactory.
 *
 * Spring Boot 3.5 (Framework 6.2): setConnectTimeout(int) and
 *   setConnectionRequestTimeout(int) exist (deprecated since 6.1 in favour
 *   of the Duration variants).
 * Spring Boot 4.0 (Framework 7.0): the deprecated int variants are removed —
 *   this class no longer compiles.
 *
 * Fix: setConnectTimeout(Duration.ofSeconds(5)) — available since 6.1,
 * so it can be adopted before the migration.
 */
public class HttpComponentsUsage {

    public static HttpComponentsClientHttpRequestFactory configureTimeout() {
        HttpComponentsClientHttpRequestFactory factory = new HttpComponentsClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
        factory.setConnectionRequestTimeout(5000);
        return factory;
    }
}
