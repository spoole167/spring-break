package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * Boot 3.5 auto-configures a Hazelcast-backed Spring Session repository via
 * HazelcastSessionConfiguration in spring-boot-autoconfigure. Boot 4.0
 * removed that support (the Hazelcast team owns the integration now), so a
 * Boot 3.5 app arriving on 4.0 gets NoSuchBeanDefinitionException for
 * SessionRepository at startup.
 *
 * Resource lookup rather than Class.forName: the configuration classes link
 * against spring-session/hazelcast types this module does not depend on.
 */
class HazelcastSessionRemovedTest {

    private static final String BASE = "org/springframework/boot/autoconfigure/session/";

    @Test
    void hazelcastSessionConfigurationShipsWithBoot() {
        assertNotNull(getClass().getClassLoader().getResource(BASE + "HazelcastSessionConfiguration.class"),
                "Boot no longer auto-configures Hazelcast-backed Spring Session. "
                + "Use Hazelcast's own spring-session integration and configure the "
                + "SessionRepository explicitly.");
    }

    @Test
    void hazelcastSessionPropertiesShipWithBoot() {
        assertNotNull(getClass().getClassLoader().getResource(BASE + "HazelcastSessionProperties.class"),
                "spring.session.hazelcast.* properties are no longer bound by Boot 4.0.");
    }
}
