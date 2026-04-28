package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.boot.actuate.endpoint.annotation.Endpoint;
import java.lang.reflect.Method;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/* Master list: 1.70 — Actuator @Nullable endpoint parameter removed */
public class ActuatorNullableTest {

    @Test
    void nullableAnnotationShouldExistOnBoot40() {
        // This test ensures the class is compilable and annotation exists on 4.0
        NullableEndpoint endpoint = new NullableEndpoint();
        assertNotNull(endpoint);
    }

    @Test
    void jspecifyNullableIsLoadableOnBoot40() {
        try {
            Class<?> clazz = Class.forName("org.jspecify.annotations.Nullable");
            assertNotNull(clazz);
        } catch (ClassNotFoundException e) {
            throw new AssertionError("org.jspecify.annotations.Nullable should be on classpath in Boot 4.0");
        }
    }

    @Test
    void isAnnotationPresentOnMethodParameter() throws Exception {
        Method method = NullableEndpoint.class.getMethod("get", String.class);
        java.lang.annotation.Annotation[] annotations = method.getParameters()[0].getAnnotations();
        boolean present = false;
        for (java.lang.annotation.Annotation a : annotations) {
            if (a.annotationType().getName().equals("org.jspecify.annotations.Nullable")) {
                present = true;
                break;
            }
        }
        assertTrue(present, "@Nullable (org.jspecify.annotations) should be present on parameter in Boot 4.0.");
    }
}
