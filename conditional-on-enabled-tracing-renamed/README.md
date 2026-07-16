# `@ConditionalOnEnabledTracing` Renamed (Tier 1: Won't Compile)

**Summary**: Spring Boot 4.0 renames `@ConditionalOnEnabledTracing` to `@ConditionalOnEnabledTracingExport`, paired with the matching property rename. User code, library code, or starter modules that reference the old annotation directly fail to compile against Boot 4.0.

## What breaks

The official Spring Boot 4.0 Migration Guide states:

> `ConditionalOnEnabledTracing` has been renamed to `ConditionalOnEnabledTracingExport`.

The class `org.springframework.boot.actuate.autoconfigure.tracing.ConditionalOnEnabledTracing` no longer exists in Boot 4.0. Any code that imports the old annotation fails at `javac`. Application code rarely references this annotation directly. The break mostly hits starter authors and corporate platform teams who mirrored Boot's gating idiom in their own conditional configuration.

## How this test works

The module declares a `@Configuration @ConditionalOnEnabledTracing` class: the kind of code a third-party starter or platform team would write to gate a tracing-only extension. The proof lives entirely at the compile layer. If the user code compiles, the Boot version still has the old annotation; if `javac` fails, the rename has landed.

- **UserTracingExtension.java**: the user-defined `@Configuration` class importing `@ConditionalOnEnabledTracing`
- **TracingApp.java**: minimal `@SpringBootApplication`
- **ConditionalOnEnabledTracingRenamedTest.java**: a context-loads test that verifies the application starts. We deliberately do NOT assert on the conditional bean firing at runtime. Spring Boot's test infrastructure overrides `management.tracing.enabled=false` by default to suppress observability noise, and the opt-out (`@AutoConfigureObservability`) is itself Boot-version-fragile. Compile success is the load-bearing assertion; the runtime test only proves the module is wired into the suite.

Run `mvn test` on Boot 3.5.16 and `UserTracingExtension` compiles, the conditional fires, and the marker bean lands in the context. Run `mvn compile -Dspring-boot.version=4.0.7` and the build stops before tests are compiled or run:

```
[ERROR] UserTracingExtension.java:[3,62]
  package org.springframework.boot.actuate.autoconfigure.tracing does not exist
[ERROR] UserTracingExtension.java:[25,2]
  cannot find symbol
  symbol: class ConditionalOnEnabledTracing
```

On Boot 3.5.16: builds and passes. On Boot 4.0.7: compile fails, `cannot find symbol: class ConditionalOnEnabledTracing`. Verified 15 July 2026.

## Fix / Migration Path

Rename the import and the annotation:

```diff
- import org.springframework.boot.actuate.autoconfigure.tracing.ConditionalOnEnabledTracing;
+ import org.springframework.boot.actuate.autoconfigure.tracing.ConditionalOnEnabledTracingExport;

  @Configuration
- @ConditionalOnEnabledTracing
+ @ConditionalOnEnabledTracingExport
  public class UserTracingExtension {
      ...
  }
```

If the user-defined configuration also reads the legacy property `management.tracing.enabled` directly, rename that to `management.tracing.export.enabled`. The sibling module **tracing-export-property-renamed** shows what happens when the property rename is left unfixed.

## Note on Boot test infrastructure

Spring Boot's `@SpringBootTest` injects a synthetic `test` PropertySource that defaults `management.tracing.enabled=false` to suppress observability noise during test runs. The opt-out is `@AutoConfigureObservability`. Without it, this module's `@ConditionalOnEnabledTracing` would be evaluated against the test default of `false` and the marker bean would never be wired, even on Boot 3.5. Teams whose tests depend on tracing being active should know this default; it bites independently of the rename.

## References

- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide), search for `ConditionalOnEnabledTracing`
- Sibling module: `tracing-export-property-renamed` (the property rename, Tier 3)
