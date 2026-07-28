package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/* On Boot 4.0 this module never reaches the test phase: compilation of
   RetryCustomizerUsage fails because RabbitRetryTemplateCustomizer is gone. */
class AmqpRetryCustomizerTest {

    @Test
    void customizerCanBeCreated() {
        assertNotNull(new RetryCustomizerUsage().retryCustomizer());
    }
}
