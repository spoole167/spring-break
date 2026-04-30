package com.example;

import org.hibernate.EmptyInterceptor;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/* Master list: 1.53 — Hibernate EmptyInterceptor removed */
public class HibernateInterceptorTest {

    @Test
    void emptyInterceptorShouldExistOnBoot35() {
        // Direct usage — fails to compile on Boot 4.0
        MyHibernateInterceptor interceptor = new MyHibernateInterceptor();
        assertNotNull(interceptor);
    }
}
