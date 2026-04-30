package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.security.saml2.provider.service.authentication.OpenSaml4AuthenticationProvider;

import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * Verifies that OpenSaml4AuthenticationProvider exists on the classpath.
 *
 * Spring Boot 3.5: class exists in spring-security-saml2-service-provider — compiles fine.
 * Spring Boot 4.0: class removed (only OpenSAML 5 supported) — fails to compile.
 */
class OpenSaml4RemovedTest {

    @Test
    void openSaml4AuthenticationProviderShouldExistOnClasspath() {
        // Direct class reference — fails to compile on Boot 4.0.
        // OpenSaml4AuthenticationProvider is removed; only OpenSAML 5 is supported.
        assertNotNull(OpenSaml4AuthenticationProvider.class.getName());
    }
}
