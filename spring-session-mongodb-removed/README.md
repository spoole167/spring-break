# Spring Session MongoDB Auto-Configuration Removed (Tier 2: Won't Run)

**Summary**: Boot 4.0 removes `MongoSessionConfiguration` and
`MongoReactiveSessionConfiguration` from spring-boot-autoconfigure (Spring Data
MongoDB owns the integration now). A Boot 3.5 app using MongoDB-backed Spring
Session fails at startup on 4.0 with
`NoSuchBeanDefinitionException: SessionRepository`.

## How this test works

No MongoDB server needed: resource lookups assert Boot's own configuration
classes (imperative and reactive) ship with the version under test.

- Boot 3.5.16: both classes present, tests pass.
- Boot 4.0.x: both gone, tests fail.

Verified 2026-07-27 on 3.5.16 (pass) and 4.0.7 (fail).
