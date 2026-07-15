# Spring Batch listener classes broken by Batch 6 package relocations (Tier 1: Won't Compile)

**Summary**: Spring Batch 6 (the version behind Spring Boot 4.0) reorganised its core packages. Domain classes such as `JobExecution` no longer live at `org.springframework.batch.core`, and the `*ListenerSupport` convenience base classes that many teams extended are gone from their old locations too. Any listener written against the Batch 5 package layout fails to compile on Boot 4.0.

## What breaks

In Spring Boot 3.5 (Spring Batch 5.x), a job listener written like this compiles fine:

```java
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.listener.JobExecutionListenerSupport;

public class JobCompletionListener extends JobExecutionListenerSupport {

    @Override
    public void afterJob(JobExecution jobExecution) {
        System.out.println("Job finished with status: " + jobExecution.getStatus());
    }
}
```

In Spring Boot 4.0 (Spring Batch 6), the old import paths no longer resolve:

```
[ERROR] cannot find symbol
  symbol:   class JobExecution
```

## How this test works

Sources live under `src/*/java/com/example/batch/` (note the nonstandard `com.example.batch` package). `JobCompletionListener` extends `JobExecutionListenerSupport` and overrides `afterJob(JobExecution)`. `StepLoggingListener` extends `StepExecutionListenerSupport` and overrides `afterStep(StepExecution)`, returning the step's `ExitStatus`. `BatchListenerClassesTest` has two tests, `jobListenerCanBeInstantiated()` and `stepListenerCanBeInstantiated()`, which simply construct each listener: their only job is to force Maven through the compile phase.

- On Boot 3.5.16: compiles and passes.
- On Boot 4.0.7: fails at compile with `cannot find symbol: class JobExecution` (Spring Batch 6 package relocations). Verified 15 July 2026.

## Fix / Migration Path

Two changes are needed:

1. Update imports for the relocated core classes: in Spring Batch 6 the domain types (`JobExecution`, `StepExecution`, `ExitStatus` and friends) have moved into per-concept subpackages under `org.springframework.batch.core`.
2. Stop extending the `*ListenerSupport` base classes. Implement the listener interfaces directly instead: `implements JobExecutionListener` and `implements StepExecutionListener`. The interfaces have had default methods since Batch 5, so you only override what you need. This change works on Boot 3.5 today, so it can be done before the migration.
