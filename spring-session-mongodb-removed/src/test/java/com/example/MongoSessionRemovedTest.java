package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * Boot 3.5 auto-configures a MongoDB-backed Spring Session repository via
 * MongoSessionConfiguration in spring-boot-autoconfigure. Boot 4.0 removed
 * that support (Spring Data MongoDB owns the integration now), so a Boot 3.5
 * app arriving on 4.0 gets NoSuchBeanDefinitionException for
 * SessionRepository at startup.
 *
 * Resource lookup rather than Class.forName: the configuration classes link
 * against spring-session/mongo types this module does not depend on.
 */
class MongoSessionRemovedTest {

    private static final String BASE = "org/springframework/boot/autoconfigure/session/";

    @Test
    void mongoSessionConfigurationShipsWithBoot() {
        assertNotNull(getClass().getClassLoader().getResource(BASE + "MongoSessionConfiguration.class"),
                "Boot no longer auto-configures MongoDB-backed Spring Session. "
                + "Configure MongoIndexedSessionRepository explicitly via "
                + "spring-session-data-mongodb.");
    }

    @Test
    void reactiveMongoSessionConfigurationShipsWithBoot() {
        assertNotNull(getClass().getClassLoader().getResource(BASE + "MongoReactiveSessionConfiguration.class"),
                "The reactive MongoDB session auto-configuration is gone too.");
    }
}
