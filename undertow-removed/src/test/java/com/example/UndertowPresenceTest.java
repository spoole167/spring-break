package com.example;

import io.undertow.Undertow;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * Smoke test so the 3.5 baseline pass is meaningful (not a zero-test run).
 * On Boot 3.5.16: spring-boot-starter-undertow resolves, Undertow is on the
 * classpath, this compiles and passes.
 * On Boot 4.0.7: the starter no longer exists in the BOM, so the module fails
 * at dependency resolution before any test runs.
 */
class UndertowPresenceTest {

    @Test
    void undertowIsOnTheClasspath() {
        assertNotNull(Undertow.builder(), "Undertow server builder should be available on Boot 3.5");
    }
}
