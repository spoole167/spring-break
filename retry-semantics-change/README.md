# Spring Retry 3.0 Semantics Change Migration Test

## One-Line Summary
Spring Retry 3.0 (Spring Boot 4.0) changes `maxAttempts=3` to mean 4 total calls instead of 3, silently affecting rate limiting, costs, and idempotency.

## What Breaks

Spring Retry 3.0 bundled with Spring Boot 4.0 changes retry count semantics:

**Spring Boot 3.4.1 (Spring Retry 2.x):** `@Retryable(maxAttempts=3)` → 3 total calls (1 initial + 2 retries)
**Spring Boot 4.0 (Spring Retry 3.x):** `@Retryable(maxRetries=3)` → 4 total calls (1 initial + 3 retries)

The parameter name changes and the count interpretation changes. This is a **silent breaking change** that affects:
- Rate-limited API clients (4 calls when rate limit is 3)
- Cloud service costs (unexpected extra invocations)
- Idempotent operation assumptions (if not truly idempotent, extra call causes problems)
- Circuit breaker thresholds (extra call may trigger breaker)
- Monitoring and alerting (unexpected call patterns)

## How This Test Works

The test suite uses Spring Boot's `@Retryable` annotation with a method that always fails, tracking invocation counts via `AtomicInteger`:

1. **testRetrySemanticChange()**: Calls an `@Retryable(maxAttempts=3)` method, catches the eventual exception, and asserts the total invocation count equals 3
2. **testRetryBehaviorExhaustion()**: Verifies that retries actually happen (invocation count > 1) and logs the actual count

The test method always throws an exception to force the retry mechanism to exhaustion, revealing the difference in count semantics between framework versions.

## On Spring Boot 3.4.1 (Spring Retry 2.x)

```bash
mvn test
```

Both tests pass. Example output:
```
✓ testRetrySemanticChange
  Total invocations: 3
  Expected 3 total invocations (maxAttempts=3) — PASS

✓ testRetryBehaviorExhaustion
  Retry mechanism triggered. Total attempts: 3
```

## On Spring Boot 4.0 (Spring Retry 3.x)

```bash
mvn test
```

First test fails. Example failure:
```
✗ testRetrySemanticChange
  Expected 3 total invocations (maxAttempts=3) but got 4.
  On Spring Boot 4.0, maxRetries changes the semantics:
  maxRetries=N means N+1 total calls, not N total calls.

✓ testRetryBehaviorExhaustion
  Retry mechanism triggered. Total attempts: 4
```

## Fix / Migration Path

### Option 1: Update Annotation to maxRetries (Explicit, Recommended)

Replace `maxAttempts` with `maxRetries` and subtract 1:

```java
// Before (Spring Retry 2.x): 3 total calls
@Retryable(maxAttempts = 3)
public void operation() { ... }

// After (Spring Retry 3.x): 3 total calls (same behavior)
@Retryable(maxRetries = 2)  // 1 initial + 2 retries
public void operation() { ... }
```

**Migration formula:** `maxRetries = maxAttempts - 1`

### Option 2: Configure Default via application.properties

Set retry defaults application-wide:

```properties
# application.properties
spring.retry.max-retries=2
```

This affects all `@Retryable` annotations without an explicit `maxRetries` parameter.

### Option 3: Use RetryTemplate Configuration

For explicit control via Spring configuration:

```java
@Configuration
public class RetryConfig {
    @Bean
    public RetryTemplate retryTemplate() {
        RetryTemplate template = new RetryTemplate();
        // SimpleRetryPolicy(maxAttempts, recoverable)
        // where maxAttempts is the TOTAL number of attempts (1 initial + retries)
        SimpleRetryPolicy policy = new SimpleRetryPolicy(3, true);
        template.setRetryPolicy(policy);
        return template;
    }
}
```

### Option 4: Update Tests to Expect New Count

If changing code is not feasible immediately, update test assertions:

```java
int expectedInvocations = 4;  // 1 initial + 3 retries on Spring Boot 4.0
assertEquals(
    expectedInvocations,
    invocations,
    "Expected " + expectedInvocations + " total invocations on Spring Boot 4.0"
);
```

## References

- Spring Retry GitHub: https://github.com/spring-projects/spring-retry
- Spring Boot 4.0 Migration Guide: https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
- Spring Boot 4.0 Release Notes: https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes
