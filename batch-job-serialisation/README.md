# Spring Batch Listener Support Classes Removed (Tier 1: Won't Compile)

JobExecutionListenerSupport, StepExecutionListenerSupport and ChunkListenerSupport removed in Spring Batch 6; implement the listener interfaces directly.

## What Breaks

Spring Batch 6.0 (Spring Boot 4.0) removes the deprecated listener "support" base classes. These were empty-method adapter classes from the pre-Java 8 era, when implementing a listener interface meant writing out every method. Since Java 8 the listener interfaces have default methods, so the adapters became dead weight. They were deprecated in Spring Batch 5.0 and are gone in 6.0.

**Classes removed:**
- `org.springframework.batch.core.listener.JobExecutionListenerSupport`
- `org.springframework.batch.core.listener.StepExecutionListenerSupport`
- `org.springframework.batch.core.listener.ChunkListenerSupport`

**Code that breaks:**
```java
public class MyJobListener extends JobExecutionListenerSupport {
    @Override
    public void afterJob(JobExecution jobExecution) { ... }
}
```

**Measured on Spring Boot 4.0.7 (clean build):**
```
[ERROR] cannot find symbol: class JobExecutionListenerSupport
```

Any class extending one of these adapters stops compiling. This is a build failure, not a runtime one.

## How This Test Works

The test references all three removed adapter classes directly:

- **BatchBuilderTest.jobExecutionListenerSupportShouldExist()**: References `JobExecutionListenerSupport.class`. Compiles on Batch 5.2 (Boot 3.5), fails to compile on Batch 6.0 (Boot 4.0).
- **BatchBuilderTest.stepExecutionListenerSupportShouldExist()**: Same pattern for `StepExecutionListenerSupport`.
- **BatchBuilderTest.chunkListenerSupportShouldExist()**: Same pattern for `ChunkListenerSupport`.

The application class (App.java) is a minimal `@SpringBootApplication` with `@EnableBatchProcessing`, so the module exercises the real Spring Batch classpath rather than a stub.

Verified 15 July 2026.

## On Spring Boot 3.5.16

```bash
mvn clean test
```

Output: All 3 tests pass. The deprecated support classes are still present in Spring Batch 5.2.

## On Spring Boot 4.0.7

Compilation of the test sources fails:
```
[ERROR] cannot find symbol: class JobExecutionListenerSupport
```

No tests run.

## Fix / Migration Path

Drop the adapter and implement the interface directly. The interfaces have default methods, so you only override what you need.

**Before (Spring Batch 5.x):**
```java
import org.springframework.batch.core.listener.JobExecutionListenerSupport;

public class MyJobListener extends JobExecutionListenerSupport {
    @Override
    public void afterJob(JobExecution jobExecution) {
        log.info("Job finished: {}", jobExecution.getStatus());
    }
}
```

**After (Spring Batch 6.0):**
```java
import org.springframework.batch.core.JobExecutionListener;

public class MyJobListener implements JobExecutionListener {
    @Override
    public void afterJob(JobExecution jobExecution) {
        log.info("Job finished: {}", jobExecution.getStatus());
    }
    // beforeJob() has a default no-op implementation; no need to override
}
```

**The mapping:**

| Removed adapter | Implement instead |
|---|---|
| `JobExecutionListenerSupport` | `JobExecutionListener` |
| `StepExecutionListenerSupport` | `StepExecutionListener` |
| `ChunkListenerSupport` | `ChunkListener` |

**Migration checklist:**

- [ ] Find all uses: `grep -rn "ListenerSupport" src/`
- [ ] Change `extends XxxListenerSupport` to `implements XxxListener`
- [ ] Remove the old imports; the interfaces live in `org.springframework.batch.core`
- [ ] Keep only the overridden methods; the defaults cover the rest
- [ ] Run `mvn clean test` to confirm

## References

- Spring Batch 6.0 Migration Guide: https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide
- Spring Batch 6.0 Release Notes: https://github.com/spring-projects/spring-batch/releases
- Spring Boot 4.0 Migration Guide: https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
