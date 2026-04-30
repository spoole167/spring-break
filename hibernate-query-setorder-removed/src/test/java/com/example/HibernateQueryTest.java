package com.example;

import org.hibernate.Session;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;
import jakarta.persistence.EntityManager;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertNotNull;

/* Master list: 1.52 — Hibernate SelectionQuery.setOrder removed */
@SpringBootTest
@Transactional
public class HibernateQueryTest {

    @SpringBootApplication
    static class TestApp {}

    @Autowired
    private EntityManager entityManager;

    @Test
    void setOrderMethodShouldExistOnBoot35() {
        Session session = entityManager.unwrap(Session.class);
        List<Product> products = HibernateQueryUsage.getOrderedProducts(session);
        assertNotNull(products);
    }

}
