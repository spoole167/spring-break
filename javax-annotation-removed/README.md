# javax.annotation Support Removed (Tier 2: Won't Run)

**Summary**: Spring Framework 7.0 (included in Spring Boot 4.0) drops support for the legacy `javax.annotation` lifecycle annotations (`@PostConstruct`, `@PreDestroy`, `@Resource`) and the `javax.inject` annotations (`@Inject`, `@Named`). Only the `jakarta.*` equivalents are recognised, as part of the move to Jakarta EE.

## What breaks

This one is nastier than a removal, because nothing visibly breaks. If your project declares `javax.annotation-api` as an explicit dependency (as this module does, and as many older projects do), the annotation classes are still on the classpath. The code compiles cleanly on 4.0. The application starts cleanly on 4.0. There is no error, no warning, no log line.

Spring just stops recognising the annotations:

1. **Lifecycle**: Methods annotated with `@javax.annotation.PostConstruct` or `@javax.annotation.PreDestroy` are silently never called.
2. **Injection**: Fields or methods annotated with `@javax.inject.Inject` are silently never injected.
3. **Resource lookup**: `@javax.annotation.Resource` no longer triggers bean lookup.

So caches never warm up, connections never initialise, cleanup never runs. The first symptom is whatever downstream failure your uninitialised state causes, which can be a long way from the actual cause.

## How this test works

The module contains:
- `JavaxLifecycleService.java`: A Spring `@Component` with `@javax.annotation.PostConstruct` and `@javax.annotation.PreDestroy` methods that set flags when called.
- `JavaxAnnotationTest.java`: A `@SpringBootTest` whose `postConstructShouldBeCalled()` test asserts the init flag was set.
- The pom declares `javax.annotation:javax.annotation-api:1.3.2` explicitly, which is why the module still compiles on 4.0.

**Measured on Spring Boot 3.5.16**: compiles and the test passes. Spring 6.x still honours the legacy annotations.

**Measured on Spring Boot 4.0.7 (clean build)**: compiles clean, the context starts without complaint, and the test fails at runtime:
```
@javax.annotation.PostConstruct was not called by Spring
```
The init method simply never ran.

Verified 15 July 2026.

## Fix / Migration Path

Switch all `javax.*` annotations to their `jakarta.*` counterparts:

- `javax.annotation.PostConstruct` -> `jakarta.annotation.PostConstruct`
- `javax.annotation.PreDestroy` -> `jakarta.annotation.PreDestroy`
- `javax.annotation.Resource` -> `jakarta.annotation.Resource`
- `javax.inject.Inject` -> `jakarta.inject.Inject`
- `javax.inject.Named` -> `jakarta.inject.Named`

Then remove the `javax.annotation-api` dependency from the pom. `jakarta.annotation-api` is managed by the Boot BOM, so no version is needed. Leaving the old javax jar on the classpath is exactly what makes this failure silent: without it you would get an honest compile error instead.

Audit for stragglers:
```bash
grep -rn "javax.annotation\|javax.inject" src/
```

## References

- [Spring Framework 7.0 Release Notes](https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Release-Notes)
- Master list entry: 1.30
