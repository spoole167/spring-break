# Tracing Auto-Configuration Relocated to its Own Module (Tier 3: Different Results)

**Summary**: Spring Boot 4.0 splits the monolithic `spring-boot-actuator-autoconfigure` into per-concern modules. The tracing auto-configuration moved to a new artifact, `spring-boot-micrometer-tracing-brave`, which `spring-boot-starter-actuator` does NOT pull in transitively. Boot 3.x apps that relied on actuator plus `micrometer-tracing-bridge-brave` to wire tracing lose tracing on Boot 4 unless they add the new module explicitly.

## What breaks

The class moved on two axes at once, package and jar:

| | Boot 3.5.16 | Boot 4.0.7 |
|---|---|---|
| Class FQN | `org.springframework.boot.actuate.autoconfigure.tracing.BraveAutoConfiguration` | `org.springframework.boot.micrometer.tracing.brave.autoconfigure.BraveAutoConfiguration` |
| Containing jar | `spring-boot-actuator-autoconfigure` | `spring-boot-micrometer-tracing-brave` (NEW) |
| Pulled in by `spring-boot-starter-actuator`? | Yes (transitively) | **No** |

The same dependency set that wired tracing on Boot 3 silently produces a tracing-free application on Boot 4. No startup error, no warning, no log line. The traces just stop arriving in your observability backend.

The same pattern affects other actuator concerns. `spring-boot-actuator-autoconfigure-4.0.7` has been dramatically slimmed; new sibling modules include:

- `spring-boot-micrometer-metrics`
- `spring-boot-micrometer-observation`
- `spring-boot-micrometer-tracing-brave`
- `spring-boot-micrometer-tracing-opentelemetry`
- `spring-boot-health`
- `spring-boot-mongodb` (host of the relocated MongoDB health indicators)

This module focuses on tracing as the most user-visible case. The broader pattern: each concern now has its own auto-configure jar that must be added explicitly.

## How this test works

The pom declares the Boot-3-era dependency set, `spring-boot-starter-actuator` plus `micrometer-tracing-bridge-brave`, and nothing more. The test asserts that `BraveAutoConfiguration` is reachable on the classpath via `Class.forName(...)`, checking both the Boot-3 package and the Boot-4 package. If neither resolves, tracing is not wired.

Run `mvn test` on Boot 3.5.16 and the Boot-3 `BraveAutoConfiguration` is on the classpath via `spring-boot-actuator-autoconfigure`; the test passes. Run `mvn test -Dspring-boot.version=4.0.7` and the test fails:

```
BraveAutoConfiguration should be reachable on the classpath. ...
Found: oldPath=false newPath=false
```

Neither the old (`actuate.autoconfigure.tracing`) nor the new (`micrometer.tracing.brave.autoconfigure`) `BraveAutoConfiguration` is on the classpath, because `spring-boot-starter-actuator` on Boot 4 pulls in neither.

On Boot 3.5.16: test passes. On Boot 4.0.7: test fails with `Found: oldPath=false newPath=false`. Verified 15 July 2026.

## Fix / Migration Path

Add the new module as an explicit dependency:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-micrometer-tracing-brave</artifactId>
</dependency>
```

For OpenTelemetry users, the equivalent is `spring-boot-micrometer-tracing-opentelemetry`. Both are managed by the Boot 4 BOM, so no version is needed.

Empirically verified: with `spring-boot-micrometer-tracing-brave:4.0.7` added, the new-package `BraveAutoConfiguration` is on the classpath and tracing auto-configures normally.

## References

- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- Sibling module: `auto-configure-observability-removed` (the test annotation removed alongside this restructure)
