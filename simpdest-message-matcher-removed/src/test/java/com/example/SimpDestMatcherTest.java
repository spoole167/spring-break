package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/* Master list: 1.59 — SimpDestMessageMatcher removed. */
class SimpDestMatcherTest {

    @Test
    void matcherShouldExistOnBoot35() {
        Object matcher = SimpDestUsage.createMatcher();
        assertNotNull(matcher);
    }
}
