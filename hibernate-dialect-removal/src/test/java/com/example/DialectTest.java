package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import org.hibernate.dialect.MySQL8Dialect;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Demonstrates the Hibernate dialect removal breaking change in Hibernate 7.0.
 *
 * BREAKING CHANGE: Version-specific dialect classes removed.
 *
 * Hibernate 6.x (Spring Boot 3.5):
 *   - MySQL8Dialect, PostgreSQL10Dialect, etc. exist (deprecated)
 *   - Application can set spring.jpa.properties.hibernate.dialect=...Dialect
 *
 * Hibernate 7.0 (Spring Boot 4.0):
 *   - All version-specific dialects removed
 *   - ClassNotFoundException if application.properties uses old dialect name
 *   - Hibernate auto-detects dialect from JDBC driver metadata
 *
 * IMPACT: Applications that explicitly configure versioned dialects fail at
 * startup before any code executes.
 *
 * MIGRATION: Remove explicit dialect configuration or use generic dialects
 * (MySQLDialect, PostgreSQLDialect) instead of version-specific ones.
 *
 * Reference: https://docs.jboss.org/hibernate/orm/7.0/migration-guide/migration-guide.html
 */
@SpringBootTest
public class DialectTest {

    @Autowired
    private ProductRepository productRepository;

    @Test
    public void testCreateAndRetrieveProduct() {
        Product product = new Product("Laptop", 999.99, 10);
        Product saved = productRepository.save(product);

        assertNotNull(saved.getId());
        assertEquals("Laptop", saved.getName());
        assertEquals(999.99, saved.getPrice());
        assertEquals(10, saved.getQuantity());
    }

    @Test
    public void testFindProductById() {
        Product product = new Product("Mouse", 29.99, 50);
        Product saved = productRepository.save(product);

        Product found = productRepository.findById(saved.getId()).orElse(null);

        assertNotNull(found);
        assertEquals("Mouse", found.getName());
    }

    /**
     * BREAKING CHANGE TEST: Verify version-specific dialect class is available.
     *
     * Many production applications have application.properties like:
     *   spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQL8Dialect
     *
     * Hibernate 6.x: MySQL8Dialect exists (deprecated) — compiles and loads fine.
     * Hibernate 7.0: MySQL8Dialect removed — fails to compile on Boot 4.0.
     *
     * The properties-based reference fails at runtime; this test makes the same
     * removal visible at compile time.
     *
     * MIGRATION: Remove explicit dialect configuration or replace with generic
     * dialect (MySQLDialect, PostgreSQLDialect). Hibernate auto-detects from JDBC.
     *
     * Reference: https://docs.jboss.org/hibernate/orm/7.0/migration-guide/migration-guide.html
     */
    @Test
    public void versionSpecificDialectClassShouldBeLoadable() {
        // Direct class reference — fails to compile on Hibernate 7.0 (Boot 4.0).
        assertNotNull(MySQL8Dialect.class.getName());
    }
}
