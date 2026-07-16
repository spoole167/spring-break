# `management.tracing.enabled` Silently Renamed (Tier 3: Different Results)

**Summary**: Spring Boot 4.0 renames `management.tracing.enabled` to `management.tracing.export.enabled`. Boot 4 ignores the legacy property: no warning, no error. A Boot 3.x application that explicitly *disabled* tracing in non-production environments starts exporting trace context again after the upgrade.

## What breaks

The official Spring Boot 4.0 Migration Guide states:

> The property `management.tracing.enabled` has been renamed to `management.tracing.export.enabled`.

Boot 4.0 does not log a deprecation warning, does not honour the legacy property, and does not migrate it for you. The legacy key is treated as an unknown property. The new key falls back to its default of `true` when tracing dependencies are present. The result: an environment that disabled tracing on Boot 3.x has tracing re-enabled on Boot 4.0.

## How this test works

The module sets `management.tracing.enabled=false` in `application.properties` (the legacy form). It then asserts that Brave's `propagationFactory` bean, which is gated by `@ConditionalOnEnabledTracing`, is NOT wired. A noop `Propagation.Factory` should be in the context as the fallback.

- **TracingApp.java**: minimal `@SpringBootApplication`
- **application.properties**: sets the legacy `management.tracing.enabled=false`
- **TracingExportPropertyRenameTest.java**: asserts `propagationFactory` is absent and `noopPropagationFactory` is present
- **pom.xml**: depends on `spring-boot-starter-actuator` plus `micrometer-tracing-bridge-brave`. A Maven profile, activated by `-Dspring-boot.version=4.0.7`, adds `spring-boot-micrometer-tracing-brave` because Boot 4's modular actuator won't load tracing auto-config without it. The profile pins that jar's version, so the pin must track the suite's target Boot 4 version.

Run `mvn test` on Boot 3.5.16 and `@ConditionalOnEnabledTracing` reads `management.tracing.enabled=false`, skips Brave's real propagation factory, and wires the noop fallback; the test passes. Run `mvn test -Dspring-boot.version=4.0.7` and the test fails:

```
TracingExportPropertyRenameTest.legacyPropertyDisablesPropagationFactory:66
  When management.tracing.enabled=false the real propagationFactory bean
  (gated by @ConditionalOnEnabledTracing) should NOT be wired.
  expected: <false> but was: <true>
```

Boot 4.0 discards the legacy property. `@ConditionalOnEnabledTracingExport` reads the new property name, finds it unset, applies its default of `true`, and wires Brave's real propagation factory despite the user's intent to disable tracing.

On Boot 3.5.16: test passes, noop fallback wired. On Boot 4.0.7: test fails, `expected: <false> but was: <true>`. Verified 15 July 2026.

## Fix / Migration Path

Rename the property in every `application.properties`, `application.yml`, environment-variable mapping, and external configuration source:

```diff
- management.tracing.enabled=false
+ management.tracing.export.enabled=false
```

The corresponding annotation was renamed too: `@ConditionalOnEnabledTracing` is now `@ConditionalOnEnabledTracingExport`. See the sibling test module **conditional-on-enabled-tracing-renamed** for the compile break that user code referencing the old annotation hits.

## Scope of proof

This test proves the property regression. It does **not** quantify the cost of accidentally re-enabled tracing (extra latency, exporter network traffic, observability backend cost): that is environment-specific. The test proves the property is lost; the operational impact is for the migrating team to assess.

## References

- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide), search for `management.tracing.enabled`
- [Spring Framework 7 observation conventions](https://github.com/spring-projects/spring-framework/wiki/Upgrading-to-Spring-Framework-7.x)
- Sibling module: `conditional-on-enabled-tracing-renamed` (annotation-rename compile break)
