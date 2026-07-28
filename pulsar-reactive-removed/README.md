# Reactive Pulsar Auto-Configuration Removed (Tier 2: Won't Run)

**Summary**: Spring Boot 4.0 removes `PulsarReactiveAutoConfiguration` (and
`spring-boot-starter-pulsar-reactive`). Apps relying on the auto-configured
`ReactivePulsarTemplate` / `ReactivePulsarClient` beans fail at runtime with
`NoSuchBeanDefinitionException`.

## How this test works

No Pulsar broker needed: the test asserts the auto-configuration class file
ships with Boot (resource lookup, since the class links against spring-pulsar
types this module doesn't depend on).

- Boot 3.5.16: class present in spring-boot-autoconfigure, test passes.
- Boot 4.0.x: class gone, test fails.

Verified 2026-07-27 on 3.5.16 (pass) and 4.0.7 (fail).
