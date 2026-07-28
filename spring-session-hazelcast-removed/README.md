# Spring Session Hazelcast Auto-Configuration Removed (Tier 2: Won't Run)

**Summary**: Boot 4.0 removes `HazelcastSessionConfiguration` and
`HazelcastSessionProperties` from spring-boot-autoconfigure (the Hazelcast team
owns the integration now). A Boot 3.5 app using Hazelcast-backed Spring Session
fails at startup on 4.0 with `NoSuchBeanDefinitionException: SessionRepository`,
and `spring.session.hazelcast.*` properties are no longer bound.

## How this test works

No Hazelcast cluster needed: resource lookups assert Boot's own configuration
classes ship with the version under test.

- Boot 3.5.16: both classes present, tests pass.
- Boot 4.0.x: both gone, tests fail.

Verified 2026-07-27 on 3.5.16 (pass) and 4.0.7 (fail).
