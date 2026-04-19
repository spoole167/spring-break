package com.example;

import jakarta.persistence.EntityManager;
import jakarta.persistence.Query;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests Hibernate query type requirement change between Boot versions.
 *
 * Hibernate 6.x (Boot 3.5): Allowed untyped queries without result type.
 *   createQuery("SELECT p FROM Product p") → works
 *
 * Hibernate 7.x (Boot 4.0): Requires explicit result type parameter.
 *   createQuery("SELECT p FROM Product p") → IllegalArgumentException
 *   createQuery("SELECT p FROM Product p", Product.class) → works
 *
 * This is a Tier 1 failure: runtime exception on first query execution.
 *
 * Test behavior:
 * - Boot 3.5: Both tests pass (typed and untyped queries work)
 * - Boot 4.0: First test passes (typed query), second test fails (untyped query)
 *
 * Fix: Add result type parameter to all createQuery() calls.
 *
 * References:
 * - Hibernate 7.0 Migration Guide: https://docs.jboss.org/hibernate/orm/7.0/migration-guide/migration-guide.html
 * - Hibernate ORM 7.0 Release: https://in.relation.to/2024/11/22/orm-700-final/
 */
@SpringBootTest
@Transactional
public class QueryTypeTest {

    @Autowired
    private EntityManager entityManager;

    @Test
    void typedQueryShouldWork() {
        // Create and persist a product
        Product product = new Product("Laptop", 999.99);
        entityManager.persist(product);
        entityManager.flush();

        // Typed query — works on both Hibernate 6.x and 7.x
        Query query = entityManager.createQuery("SELECT p FROM Product p", Product.class);
        List<Product> results = query.getResultList();

        assertNotNull(results);
        assertEquals(1, results.size());
        assertEquals("Laptop", results.get(0).getName());
    }

    @Test
    void untypedQueryShouldWork() {
        // Create and persist a product
        Product product = new Product("Mouse", 29.99);
        entityManager.persist(product);
        entityManager.flush();

        // Untyped query — works on Hibernate 6.x, fails on Hibernate 7.x
        // On Boot 4.0 (Hibernate 7.x), this throws:
        //   java.lang.IllegalArgumentException: createQuery() requires a result type
        Query query = entityManager.createQuery("SELECT p FROM Product p");
        List results = query.getResultList();

        assertNotNull(results);
        assertEquals(1, results.size());
    }
}
