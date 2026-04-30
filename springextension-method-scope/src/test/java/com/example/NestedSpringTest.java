package com.example;

import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.TestContext;
import org.springframework.test.context.TestExecutionListener;
import org.springframework.test.context.TestExecutionListeners;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * Demonstrates the SpringExtension scope change in Spring Framework 7.0 (Boot 4.0).
 *
 * Spring Framework 6.x (Boot 3.5): SpringExtension uses TEST_CLASS scope.
 *   TestContextManagers are stored in the shared root ExtensionContext store, keyed
 *   by test class. Each class (outer + inner) gets one TestContextManager, and
 *   beforeTestClass() is called exactly once per class — 2 calls total here.
 *
 * Spring Framework 7.0 (Boot 4.0): SpringExtension uses TEST_METHOD scope by default.
 *   TestContextManagers are stored in per-method ExtensionContext stores. Each test
 *   method creates its own TestContextManager, so beforeTestClass() fires once per
 *   method rather than once per class — 3 calls total here (1 outer + 2 inner).
 *
 * This is the concrete impact: custom TestExecutionListeners that initialise state in
 * beforeTestClass() expecting it to run once per class will see it called once per
 * method on Boot 4.0, corrupting or duplicating any class-level setup logic.
 *
 * Fix: annotate the outer class with
 *   @SpringExtensionConfig(useTestClassScopedExtensionContext = true)
 * to restore Boot 3.5 behavior.
 *
 * Master list: 2.14
 * Reference: https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Migration-Guide
 */
@ExtendWith(SpringExtension.class)
@ContextConfiguration(classes = NestedSpringTest.TestConfig.class)
@TestExecutionListeners(
        listeners = NestedSpringTest.ClassSetupTracker.class,
        mergeMode = TestExecutionListeners.MergeMode.MERGE_WITH_DEFAULTS
)
class NestedSpringTest {

    /**
     * Counts how many times beforeTestClass() is invoked across the class hierarchy.
     *
     * Boot 3.5 (class scope): one call per test class.
     *   Outer class + Inner class = 2 calls total.
     *
     * Boot 4.0 (method scope): one call per test method.
     *   1 outer method + 2 inner methods = 3 calls total.
     */
    static class ClassSetupTracker implements TestExecutionListener {
        static final AtomicInteger callCount = new AtomicInteger(0);

        @Override
        public void beforeTestClass(TestContext testContext) {
            callCount.incrementAndGet();
        }
    }

    @Autowired
    ApplicationContext applicationContext;

    @Test
    void outerContextIsAvailable() {
        assertNotNull(applicationContext);
    }

    @Nested
    @TestMethodOrder(MethodOrderer.OrderAnnotation.class)
    class InnerTests {

        @Autowired
        ApplicationContext applicationContext;

        @Test
        @Order(1)
        void innerContextIsAvailable() {
            assertNotNull(applicationContext);
        }

        @Test
        @Order(2)
        void beforeTestClassCalledOncePerClassNotPerMethod() {
            // Runs last so all test methods have already triggered their
            // TestContextManager lookups before we check the count.
            //
            // Boot 3.5 (class scope): TestContextManagers stored in the shared root store,
            // keyed by class. One created for outer class, one for inner class = 2 total.
            // beforeTestClass() called exactly twice regardless of method count.
            //
            // Boot 4.0 (method scope): each method gets its own store entry.
            // 1 outer method + 2 inner methods = 3 TestContextManagers = 3 calls.
            // This assertion fails on Boot 4.0.
            //
            // Fix: @SpringExtensionConfig(useTestClassScopedExtensionContext = true)
            assertEquals(2, ClassSetupTracker.callCount.get(),
                    "On Boot 3.5, beforeTestClass() is called once per test class " +
                    "(2 total: outer + inner), because SpringExtension uses class-scoped " +
                    "TestContextManagers. On Boot 4.0, each test method creates its own " +
                    "TestContextManager, so beforeTestClass() fires once per method (3 total) " +
                    "— breaking any listener that expects a single class-level initialisation.");
        }
    }

    @Configuration
    static class TestConfig {
        @Bean
        String testValue() {
            return "test";
        }
    }
}
