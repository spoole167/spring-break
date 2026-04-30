package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.batch.core.job.builder.JobBuilder;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/* Master list: 1.68 — Spring Batch JobBuilder(String) constructor removed */
public class JobBuilderTest {

    @Test
    void jobBuilderConstructorShouldExistOnBoot35() {
        // Direct usage — fails to compile on Boot 4.0
        JobBuilder builder = JobBuilderUsage.createBuilder("testJob");
        assertNotNull(builder);
    }
}
