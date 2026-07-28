package com.example.app;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;

import com.example.legacylib.LegacyAutoConfiguration.LegacyMarker;
import com.example.legacylib.ModernAutoConfiguration.ModernMarker;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * NEGATIVE RESULT — verified 2026-07-27 on Boot 3.5.16.
 *
 * The proposed cheat-sheet card claimed Boot 4.0 stops honouring
 * auto-configuration entries in META-INF/spring.factories. This module
 * proves the mechanism is ALREADY dead on Boot 3.5: the entry is ignored
 * there too (registration support was removed in Boot 3.0).
 *
 * Therefore this is NOT a 3.5 -> 4.0 break and has no card. The module is
 * kept as documentation: both tests pass on BOTH Boot versions, unlike
 * every other module in this suite.
 *
 * - ModernMarker: registered ONLY in META-INF/spring/AutoConfiguration.imports
 *   -> present on 3.5 and 4.0.
 * - LegacyMarker: registered ONLY in META-INF/spring.factories under the
 *   EnableAutoConfiguration key -> absent on 3.5 and 4.0.
 */
@SpringBootTest
class SpringFactoriesAutoConfigTest {

    @Autowired
    ApplicationContext context;

    @Test
    void modernImportsFileIsHonoured() {
        assertEquals(1, context.getBeanNamesForType(ModernMarker.class).length,
                "AutoConfiguration.imports registration should work on every Boot version since 2.7");
    }

    @Test
    void legacySpringFactoriesIsIgnoredOnBothVersions() {
        assertEquals(0, context.getBeanNamesForType(LegacyMarker.class).length,
                "spring.factories EnableAutoConfiguration registration died in Boot 3.0. "
                + "If this bean appears, the negative result no longer holds and the "
                + "cheat-sheet needs revisiting.");
    }
}
