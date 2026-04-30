package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/* Master list: 1.44 — StreamsBuilderFactoryBeanCustomizer removed. */
class KafkaCustomizerTest {

    @Test
    void customizerCanBeInstantiated() {
        KafkaCustomizerUsage usage = new KafkaCustomizerUsage();
        assertNotNull(usage);
    }
}
