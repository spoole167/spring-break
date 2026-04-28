package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.boot.actuate.endpoint.annotation.Endpoint;
import java.lang.reflect.Method;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/* Master list: 1.70 — Actuator @Nullable endpoint parameter removed */
public class ActuatorNullableTest {

    @Test
    void nullableAnnotationShouldExistOnBoot35() {
        // This test ensures the class is compilable and annotation exists on 3.5
        NullableEndpoint endpoint = new NullableEndpoint();
        assertNotNull(endpoint);
    }

    @Test
    void springNullableIsLoadableOnBoot35() {
        try {
            Class<?> clazz = Class.forName("org.springframework.lang.Nullable");
            assertNotNull(clazz);
        } catch (ClassNotFoundException e) {
            throw new AssertionError("org.springframework.lang.Nullable should be on classpath in Boot 3.5");
        }
    }

    @Test
    void isAnnotationPresentOnMethodParameter() throws Exception {
        Method method = NullableEndpoint.class.getMethod("get", String.class);
        java.lang.annotation.Annotation[] annotations = method.getParameters()[0].getAnnotations();
        boolean present = false;
        for (java.lang.annotation.Annotation a : annotations) {
            if (a.annotationType().getName().equals("org.springframework.lang.Nullable")) {
                present = true;
                break;
            }
        }
        assertTrue(present, "@Nullable (org.springframework.lang) should be present on parameter in Boot 3.5. " +
                "In Boot 4.0 it is no longer supported and should be replaced by org.jspecify.annotations.Nullable.");
    }
}
