package com.example;

import org.hibernate.annotations.Where;
import org.hibernate.annotations.OrderBy;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/* Master list: 1.51 — Hibernate @Where and @OrderBy removed */
public class HibernateAnnotationsTest {

    @Test
    void annotationsShouldExistOnBoot35() {
        // Direct class references — fail to compile on Boot 4.0 when annotations are removed
        assertNotNull(Where.class.getName());
        assertNotNull(OrderBy.class.getName());
    }
}
