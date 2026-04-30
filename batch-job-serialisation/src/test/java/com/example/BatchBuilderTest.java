package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.batch.core.listener.JobExecutionListenerSupport;
import org.springframework.batch.core.listener.StepExecutionListenerSupport;
import org.springframework.batch.core.listener.ChunkListenerSupport;

import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * Demonstrates Spring Batch 6.0 removal of deprecated listener support classes.
 *
 * Spring Batch 5.2 (Spring Boot 3.5):
 *   - JobExecutionListenerSupport exists (deprecated since 5.0)
 *   - StepExecutionListenerSupport exists (deprecated since 5.0)
 *   - ChunkListenerSupport exists (deprecated since 5.0)
 *
 * Spring Batch 6.0 (Spring Boot 4.0):
 *   - All three classes removed entirely — fails to compile.
 *
 * Fix: Implement the listener interfaces directly. Since Java 8, interfaces
 * can have default methods, making these base classes unnecessary.
 *
 * Reference: https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide
 */
public class BatchBuilderTest {

    @Test
    void jobExecutionListenerSupportShouldExist() {
        // Direct class reference — fails to compile on Spring Batch 6.0 (Boot 4.0).
        // Implement JobExecutionListener directly instead.
        assertNotNull(JobExecutionListenerSupport.class.getName());
    }

    @Test
    void stepExecutionListenerSupportShouldExist() {
        // Direct class reference — fails to compile on Spring Batch 6.0 (Boot 4.0).
        // Implement StepExecutionListener directly instead.
        assertNotNull(StepExecutionListenerSupport.class.getName());
    }

    @Test
    void chunkListenerSupportShouldExist() {
        // Direct class reference — fails to compile on Spring Batch 6.0 (Boot 4.0).
        // Implement ChunkListener directly instead.
        assertNotNull(ChunkListenerSupport.class.getName());
    }
}
