# `@AutoConfigureObservability` Removed (Tier 1: Won't Compile)

**Summary**: Spring Boot 4.0 removes `org.springframework.boot.test.autoconfigure.actuate.observability.AutoConfigureObservability` entirely. Tests that opt into observability with this annotation fail to compile on Boot 4. The annotation is gone, along with the suppression mechanism it opted out of.

## What breaks

In Spring Boot 3.x, `spring-boot-test-autoconfigure` ships an `ObservabilityContextCustomizerFactory`. It injects a `test` PropertySource into `@SpringBootTest` runs, defaulting `management.tracing.enabled=false` to suppress observability noise during tests. `@AutoConfigureObservability` is the opt-out: applying it to a test class re-enables observability for that test.

In Spring Boot 4.0:
- The annotation is removed from `spring-boot-test-autoconfigure`.
- The `ObservabilityContextCustomizerFactory` mechanism is also removed.
- Tests that imported the annotation fail at `javac`.

Empirically verified by grepping every `spring-boot-*-4.0.7.jar` in the Maven cache: zero matches for `AutoConfigureObservability`.

## How this test works

`ObservabilityIntegrationTest` imports the annotation and applies it to a `@SpringBootTest` class:

```java
import org.springframework.boot.test.autoconfigure.actuate.observability.AutoConfigureObservability;

@SpringBootTest
@AutoConfigureObservability
class ObservabilityIntegrationTest { ... }
```

Run `mvn test` on Boot 3.5.16 and the annotation resolves from `spring-boot-test-autoconfigure-3.5.16.jar`. Run `mvn test-compile -Dspring-boot.version=4.0.7` and `javac` reports:

```
package org.springframework.boot.test.autoconfigure.actuate.observability does not exist
cannot find symbol
```

On Boot 3.5.16: compiles, runs, passes. On Boot 4.0.7: compile fails on the missing package. Verified 15 July 2026.

## Fix / Migration Path

**Delete the annotation.** Boot 4 removed both the annotation and the suppression mechanism, so there is nothing to swap in. Tests that used `@AutoConfigureObservability` to opt into observability on Boot 3 need no opt-in on Boot 4, because the default suppression no longer happens.

```diff
- @SpringBootTest
- @AutoConfigureObservability
- class MyTest { ... }
+ @SpringBootTest
+ class MyTest { ... }
```

Watch for the adjacent break: tracing auto-configuration itself may not fire on Boot 4 with the old dependency set. `spring-boot-starter-actuator` plus `micrometer-tracing-bridge-brave` is no longer enough. See sibling module **tracing-autoconfig-relocated**: you need the new `spring-boot-micrometer-tracing-brave` module added explicitly.

## References

- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- Sibling module: `tracing-autoconfig-relocated`
