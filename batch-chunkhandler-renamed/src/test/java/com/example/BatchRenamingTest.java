package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.batch.integration.chunk.ChunkHandler;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/* Master list: 1.69 — Spring Batch ChunkHandler renamed and setJobLauncher removed */
public class BatchRenamingTest {

    @Test
    void chunkHandlerShouldExistOnBoot35() {
        // Direct class reference — fails to compile on Boot 4.0 when ChunkHandler is renamed
        assertNotNull(ChunkHandler.class.getName());
    }

    @Test
    void setJobLauncherShouldExistOnJobStepInBoot35() {
        // BatchRenamingUsage.configureJobStep calls jobStep.setJobLauncher(launcher) directly.
        // Fails to compile on Boot 4.0 — method removed in Spring Batch 6.0.
        assertNotNull(BatchRenamingUsage.class.getName());
    }
}
