package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/* Master list: 1.34 — HttpComponents request factory setConnectTimeout(int) removed. */
class HttpComponentsTimeoutTest {

    @Test
    void intBasedTimeoutSettersShouldConfigureFactory() {
        // Compiles and passes on Boot 3.5 (Framework 6.2).
        // On Boot 4.0 (Framework 7.0) this module fails at compile:
        //   cannot find symbol: method setConnectTimeout(int)
        assertNotNull(HttpComponentsUsage.configureTimeout());
    }
}
