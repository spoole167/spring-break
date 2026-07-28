package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * Boot 3.5 ships reactive Pulsar auto-configuration inside
 * spring-boot-autoconfigure. Boot 4.0 removes it entirely (along with
 * spring-boot-starter-pulsar-reactive): applications relying on the
 * auto-configured ReactivePulsarTemplate / ReactivePulsarClient beans fail
 * with NoSuchBeanDefinitionException at runtime.
 *
 * The test pins the root cause without needing a Pulsar broker: the
 * auto-configuration class file ships with Boot 3.5 and is gone on 4.0.
 * (Resource lookup, not Class.forName: the class links against spring-pulsar
 * types that this module deliberately does not depend on.)
 */
class PulsarReactiveRemovedTest {

    @Test
    void reactivePulsarAutoConfigurationShipsWithBoot() {
        assertNotNull(getClass().getClassLoader().getResource(
                "org/springframework/boot/autoconfigure/pulsar/PulsarReactiveAutoConfiguration.class"),
                "PulsarReactiveAutoConfiguration is gone: Boot no longer auto-configures "
                + "ReactivePulsarTemplate/ReactivePulsarClient. Add spring-pulsar-reactive "
                + "configuration manually or move to the imperative Pulsar support.");
    }
}
