# spring-jcl module removed (Tier 1: Won't Resolve)

**Summary**: For years Spring Framework shipped its own logging bridge, `org.springframework:spring-jcl`, which repackaged the Commons Logging API so Spring's internals could log without dragging in the original `commons-logging` jar. Spring Framework 7 (Spring Boot 4.0) deletes the module entirely and depends on the standard Commons Logging bridge artifact directly. Builds that declare `spring-jcl` explicitly without a version, relying on the BOM, fail at dependency resolution on Boot 4.0. Maven stops before compiling anything.

## What breaks

In Spring Boot 3.5, this version-less declaration resolves because the Boot BOM manages `spring-jcl` as part of Spring Framework:

```xml
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-jcl</artifactId>
</dependency>
```

In Spring Boot 4.0, the module no longer exists and the BOM no longer manages it, so resolution fails:

```
'dependencies.dependency.version' for org.springframework:spring-jcl:jar is missing
```

## How this test works

The pom declares `org.springframework:spring-jcl` with no version alongside `spring-boot-starter`, mimicking an application that pinned the bridge explicitly at some point (often to "fix" a logging conflict) and forgot about it. `LoggingService` uses the Commons Logging API directly: it holds a `Log` obtained from `LogFactory.getLog(...)` and its `doWork(String)` method logs and returns a processed value. `SpringJclRemovedTest` has two tests: `loggingServiceReturnsProcessedValue()` exercises `doWork("hello")`, and `springJclIsOnClasspath()` loads `org.apache.commons.logging.LogFactory` via `Class.forName` to prove the bridge supplied the API.

- On Boot 3.5.16: compiles and passes.
- On Boot 4.0.7: fails at dependency resolution, `org.springframework:spring-jcl` version missing (module removed in Spring Framework 7). Verified 15 July 2026.

## Fix / Migration Path

Delete the explicit `spring-jcl` dependency. That is the whole fix for most projects: Spring Framework 7 uses the standard Commons Logging bridge directly, so the `org.apache.commons.logging` API (`Log`, `LogFactory`) keeps working through Boot's logging starter without any code changes. `LoggingService` in this module would compile and run unmodified once the dead dependency is removed. The real lesson is to audit your pom for framework-internal artifacts you declared directly years ago: they resolve silently right up until the framework stops publishing them.
