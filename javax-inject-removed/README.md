# javax.inject annotations silently ignored (Tier 2: Won't Run)

**Summary**: Spring long treated the JSR-330 `javax.inject` annotations (`@Inject`, `@Named`) as first-class equivalents of `@Autowired` and `@Component`. Spring Framework 7 (Spring Boot 4.0) drops that support: only the `jakarta.inject` variants are recognised. The nasty part is that nothing fails at build time. If the old `javax.inject` jar is on your classpath, the code still compiles on Boot 4.0, the annotations are simply ignored, and your beans quietly never get registered. The failure only surfaces at runtime when something tries to inject them.

## What breaks

In Spring Boot 3.5, this class is a fully functional Spring bean:

```java
import javax.inject.Inject;
import javax.inject.Named;

@Named("javaxInjectService")
public class JavaxInjectService {

    @Inject
    private ApplicationContext context;
    ...
}
```

In Spring Boot 4.0, it compiles without complaint (the `javax.inject:javax.inject:1` jar is explicitly declared in the pom, so the package still exists). But Spring no longer reads `@Named`, so no bean is registered, and the test fails at context startup:

```
UnsatisfiedDependencyException: ... No qualifying bean of type 'com.example.JavaxInjectService' available
```

## How this test works

The pom declares `javax.inject:javax.inject` version 1 alongside `spring-boot-starter`, mimicking a legacy application that has carried the JSR-330 jar for years. `JavaxInjectApp` is a minimal `@SpringBootApplication`. `JavaxInjectService` is annotated `@Named("javaxInjectService")` and uses `@Inject` to receive the `ApplicationContext`. `JavaxInjectTest` is a `@SpringBootTest` that autowires `JavaxInjectService`; its single test, `injectShouldWireApplicationContext()`, asserts the context was injected.

- On Boot 3.5.16: compiles and passes.
- On Boot 4.0.7: compiles clean, then fails at runtime. The `@javax.inject.Named` bean is silently not registered and the test fails with `UnsatisfiedDependencyException: No qualifying bean of type 'JavaxInjectService'`. Verified 15 July 2026.

## Fix / Migration Path

Migrate to `jakarta.inject`:

```java
import jakarta.inject.Inject;
import jakarta.inject.Named;
```

Add `jakarta.inject:jakarta.inject-api` (version managed by the Boot BOM) and drop the old `javax.inject` jar entirely, otherwise it sits on the classpath letting broken code compile. Alternatively, switch to Spring-native annotations (`@Component`, `@Autowired`) and remove the JSR-330 dependency altogether. Both changes work on Boot 3.5 today, so do them before you migrate: this is exactly the kind of break where a green compile lulls you into shipping a broken context.
