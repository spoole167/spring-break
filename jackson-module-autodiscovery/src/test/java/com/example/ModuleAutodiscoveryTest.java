package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;

import java.lang.reflect.Method;
import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * A Money serializer module sits on the classpath registered ONLY through
 * ServiceLoader (both Jackson 2 and Jackson 3 flavours).
 *
 * Boot 3.5 / Jackson 2: Boot registers well-known modules explicitly and does
 * NOT ServiceLoader-scan. Money serializes with the default BeanSerializer:
 *   {"amount":150.00,"currency":"EUR"}                          -> test passes
 *
 * Boot 4.0 / Jackson 3: modules are found and added automatically
 * (spring.jackson.find-and-add-modules). The classpath module activates and
 * the SAME code produces:
 *   "150.00 EUR"                                                -> test fails
 *
 * No error, no warning: the JSON schema changed because a jar was present.
 * Fix on 4.0: spring.jackson.find-and-add-modules=false.
 *
 * Reflection is used because the auto-configured mapper is
 * com.fasterxml.jackson.databind.ObjectMapper on 3.5 but
 * tools.jackson.databind.ObjectMapper on 4.0. writeValueAsString exists on
 * both.
 */
@SpringBootTest
class ModuleAutodiscoveryTest {

    @Autowired
    ApplicationContext context;

    @Test
    void classpathModuleIsNotSilentlyRegistered() throws Exception {
        Object mapper = autoConfiguredMapper();
        Method write = mapper.getClass().getMethod("writeValueAsString", Object.class);
        String json = (String) write.invoke(mapper, new Money(new BigDecimal("150.00"), "EUR"));

        assertTrue(json.contains("\"currency\""),
                "Money should serialize with the default bean serializer, got: " + json);
        assertFalse(json.contains("150.00 EUR"),
                "The ServiceLoader-registered Jackson module activated by itself: "
                + "module auto-discovery silently changed the JSON output to " + json);
    }

    private Object autoConfiguredMapper() throws Exception {
        for (String cn : new String[] {
                "tools.jackson.databind.ObjectMapper",          // Jackson 3 (Boot 4.0)
                "com.fasterxml.jackson.databind.ObjectMapper"}) // Jackson 2 (Boot 3.5)
        {
            try {
                Class<?> type = Class.forName(cn);
                String[] names = context.getBeanNamesForType(type);
                if (names.length > 0) {
                    return context.getBean(names[0]);
                }
            } catch (ClassNotFoundException ignored) {
                // that Jackson generation is not on the classpath
            }
        }
        throw new IllegalStateException("No auto-configured ObjectMapper bean found");
    }
}
