# Spring Session Property Prefixes Silently Renamed (Tier 3: Different Results)

**Summary**: Spring Boot 4.0 renames Spring Session backend properties:
- `spring.session.redis.*` → `spring.session.data.redis.*`
- `spring.session.mongodb.*` → `spring.session.data.mongodb.*`

Boot 4 ignores the legacy prefixes: sessions land under default namespace and collection names rather than the configured ones. No error, no warning. The classic symptom is "users appear logged out immediately after login", because session keys are written to one namespace and looked up under another.

## What breaks

| | Boot 3.5.16 | Boot 4.0.7 |
|---|---|---|
| Properties class | `org.springframework.boot.autoconfigure.session.RedisSessionProperties` (in `spring-boot-autoconfigure`) | `org.springframework.boot.session.data.redis.autoconfigure.SessionDataRedisProperties` (in the new per-concern jar `spring-boot-session-data-redis`) |
| `@ConfigurationProperties` prefix | `spring.session.redis` | `spring.session.data.redis` |
| Setting only the legacy prefix | Honored | Silently ignored |

The MongoDB equivalent follows the same pattern: `MongoSessionProperties` renamed and moved, and the prefix gains the `data` infix.

Empirically verified by reflecting on the `@ConfigurationProperties` annotation per Boot version.

## How this test works

The test loads whichever properties class exists for the running Boot version (Boot 3's `RedisSessionProperties` or Boot 4's `SessionDataRedisProperties`) and reads the `@ConfigurationProperties` `prefix` attribute. It asserts the prefix equals `spring.session.redis`, the Boot-3 canonical value.

This sidesteps auto-config firing: Spring Session's auto-configuration has multiple conditional triggers that are hard to satisfy without a live Redis. The classpath and annotation check proves the rename without needing a working session repository.

A Maven profile, activated by `-Dspring-boot.version=4.0.7`, adds the `spring-boot-session-data-redis` jar that holds Boot 4's properties class. The profile pins that jar's version, so the pin must track the suite's target Boot 4 version.

Run `mvn test` on Boot 3.5.16 and `RedisSessionProperties` is on the classpath with prefix `spring.session.redis`; the test passes. Run `mvn test -Dspring-boot.version=4.0.7` and the test fails:

```
On Boot 3.x the canonical Spring Session Redis property prefix is 'spring.session.redis'.
On Boot 4.0 the prefix has been silently renamed to 'spring.session.data.redis' —
any application.properties using the old prefix is silently ignored.
Found prefix: 'spring.session.data.redis' on class
org.springframework.boot.session.data.redis.autoconfigure.SessionDataRedisProperties
==> expected: <spring.session.redis> but was: <spring.session.data.redis>
```

The failure message names the new class FQN and the new prefix: exactly what a migrating team needs.

On Boot 3.5.16: test passes, prefix is `spring.session.redis`. On Boot 4.0.7: test fails, `expected: <spring.session.redis> but was: <spring.session.data.redis>`. Verified 15 July 2026.

## Fix / Migration Path

```diff
- spring.session.redis.namespace=myapp:session
- spring.session.redis.flush-mode=on-save
- spring.session.redis.save-mode=on-set-attribute
+ spring.session.data.redis.namespace=myapp:session
+ spring.session.data.redis.flush-mode=on-save
+ spring.session.data.redis.save-mode=on-set-attribute
```

```diff
- spring.session.mongodb.collection-name=sessions
+ spring.session.data.mongodb.collection-name=sessions
```

`spring.session.store-type` is unchanged. Only the per-store sub-keys gain the `data` infix.

## Watch out

Sessions ARE still stored, just under the default namespace or collection name. A wrong namespace in Redis means session keys go to one place and the lookup checks another, so users appear logged out. Confirm post-migration by inspecting Redis directly (`KEYS '*:session*'`) and verifying keys sit under the configured namespace.

## References

- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- See also: `mongodb-property-renames` (the parallel rename for the main MongoDB connection; note the inverse direction: `spring.data.mongodb.*` → `spring.mongodb.*` REMOVES `data`, while session backends ADD it)
