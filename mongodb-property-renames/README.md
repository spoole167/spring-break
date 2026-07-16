# MongoDB Configuration Properties Silently Renamed (Tier 3: Different Results)

**Summary**: Spring Boot 4.0 renames `spring.data.mongodb.*` to `spring.mongodb.*`. Boot 4 ignores the legacy prefix: applications start, MongoTemplate is wired, but the URI falls back to `localhost:27017/test` rather than the configured value. No error, no warning. The likely symptom: "I configured production credentials but the app is connecting to localhost."

## What breaks

| | Boot 3.5.16 | Boot 4.0.7 |
|---|---|---|
| `MongoProperties` class | `org.springframework.boot.autoconfigure.mongo.MongoProperties` (in `spring-boot-autoconfigure`) | `org.springframework.boot.mongodb.autoconfigure.MongoProperties` (in `spring-boot-mongodb`) |
| Property prefix | `spring.data.mongodb.*` | `spring.mongodb.*` |
| Setting only the legacy prefix | Honoured: host/db/auth flow through | Ignored: defaults used |

## How this test works

`application.properties` sets only the legacy prefix:

```properties
spring.data.mongodb.uri=mongodb://nonexistent-host.test:27017/configured-db
```

The test looks up Boot's `MongoProperties` bean by simple class name, which is cross-version safe because the package differs between Boot 3 and Boot 4. It asserts the bean's `getUri()` returns the configured value.

Run `mvn test` on Boot 3.5.16 and the Mongo driver startup log shows `clusterSettings={hosts=[nonexistent-host.test:27017]...}`: the property was honoured and the test passes. Run `mvn test -Dspring-boot.version=4.0.7` and the test fails:

```
MongoProperties.getUri() should reflect the configured spring.data.mongodb.uri value on Boot 3.x.
On Boot 4.0 the property is silently ignored — rename to spring.mongodb.uri. Got: null
```

The legacy property was discarded; the new `MongoProperties` bean reads `spring.mongodb.*` only.

On Boot 3.5.16: test passes, configured host honoured. On Boot 4.0.7: test fails, `getUri()` returns `null`. Verified 15 July 2026.

## Fix / Migration Path

Rename the property prefix in every property file, environment variable, deployment manifest, secret store, and external config source:

```diff
- spring.data.mongodb.uri=mongodb://user:pass@host:27017/mydb
- spring.data.mongodb.database=mydb
- spring.data.mongodb.auto-index-creation=true
+ spring.mongodb.uri=mongodb://user:pass@host:27017/mydb
+ spring.mongodb.database=mydb
+ spring.mongodb.auto-index-creation=true
```

Actuator health properties moved similarly: `management.health.mongo.*` → `management.health.mongodb.*`.

## Watch out

Nothing fails visibly. Apps still start, MongoTemplate is wired, queries succeed against the wrong instance. Use a deliberately fail-open URI (like `nonexistent-host.test`) in non-prod to confirm the property is being read post-migration.

Spring Session MongoDB property keys changed separately: `spring.session.mongodb.*` → `spring.session.data.mongodb.*`. See sibling module `spring-session-property-renames`.

## References

- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
