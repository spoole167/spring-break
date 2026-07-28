# spring.factories Auto-Configuration Registration (NEGATIVE RESULT)

**Summary**: This module was built to verify a proposed cheat-sheet card claiming
Spring Boot 4.0 stops reading auto-configuration registrations from
`META-INF/spring.factories`. The claim is **wrong for a 3.5 → 4.0 deck**: the
mechanism is already dead on Boot 3.5 (support was removed in Boot 3.0).

## What this module proves

Two auto-configurations live outside the component-scanned package:

- `ModernAutoConfiguration` — registered only in
  `META-INF/spring/AutoConfiguration.imports`. Its bean is present on
  **both** 3.5.16 and 4.0.x.
- `LegacyAutoConfiguration` — registered only in `META-INF/spring.factories`
  under the `EnableAutoConfiguration` key. Its bean is absent on
  **both** versions.

Verified 2026-07-27 against Boot 3.5.16: the legacy entry is ignored there,
so nothing changes at 4.0. Anyone hitting this break hit it at the
2.x → 3.0 boundary, not at 3.5 → 4.0.

## Consequence for the cheat-sheets

No card. The draft card `spring-factories-autoconfig-imports` should be
removed from the deck. Both tests in this module pass on both Boot versions,
unlike every other module in this suite: it exists as documentation of the
negative result.

## References

- [Spring Boot 3.0 Migration Guide — auto-configuration registration](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)
