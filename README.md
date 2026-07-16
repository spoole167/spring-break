# Spring Boot 3.5 → 4.0 Migration Test Cases

69 self-contained Maven modules, each demonstrating a specific breaking change at the 3.5→4.0 boundary. The default build uses Spring Boot 3.5.16 — all tests pass. Override the version to see what breaks.

Last full verification: 15 July 2026 — all 69 modules pass on 3.5.16, all 69 fail on 4.0.7 (9 at dependency resolution, 41 at compile, 12 at runtime, 7 with silently different results).

## Quick start

```bash
# Everything green (Spring Boot 3.5.16)
./run-all-tests.sh

# Watch it break (Spring Boot 4.0.7)
./run-all-tests.sh -v 4.0.7

# Quiet mode (just pass/fail summary)
./run-all-tests.sh -v 4.0.7 -q

# Single module via Maven (always clean — stale target/ dirs from a previous
# version run 3.5-compiled classes against the 4.0 classpath and lie to you)
mvn clean test -pl jackson-date-serialisation

# For 4.x runs, build from inside the module directory. On 4.0 nine module
# poms lose their managed dependency versions, which makes the root reactor
# unreadable — so -pl from the root fails for every module, not just those nine.
(cd jackson-date-serialisation && mvn clean test -Dspring-boot.version=4.0.7)
```

## Modules by tier

### Tier 1 — Won't Build — 50 modules

Your build breaks immediately. Loud, obvious, caught before deploy. Highlights (see `run-all-tests.sh` for the full tier lists):

| Module | What breaks |
|--------|------------|
| `jackson-group-id` | Maven group ID changes from `com.fasterxml.jackson` to `tools.jackson` |
| `undertow-removed` | `spring-boot-starter-undertow` no longer exists |
| `security-removed-apis` | `authorizeRequests()` and `.and()` removed from Spring Security DSL |
| `deprecated-classes-removed` | APIs deprecated across 3.x lifecycle removed in 4.0 |
| `hibernate-session-delete` | `Session.delete(Object)` removed — must use `Session.remove(Object)` |
| `testcontainers-class-relocation` | `PostgreSQLContainer` moved to `org.testcontainers.postgresql` |
| `spring-retry-removed` | `spring-retry` library removed from Boot 4.0 BOM — retry moved to SF7 core |
| `batch-job-serialisation` | `JobExecutionListenerSupport`, `StepExecutionListenerSupport`, `ChunkListenerSupport` removed in Batch 6 |
| `mockbean-removed` | `@MockBean` / `@SpyBean` removed — test sources fail to compile on 4.0 |
| `hibernate-dialect-removal` | Version-specific dialects (`MySQL8Dialect`, etc.) removed from Hibernate 7 |
| `oauth-password-grant-removed` | OAuth 2.0 Password Grant removed per OAuth 2.1 — `AuthorizationGrantType.PASSWORD` gone |
| `hibernate-cascade-removal` | `CascadeType.SAVE_UPDATE` removed in Hibernate 7 — must use JPA `PERSIST` + `MERGE` |

### Tier 2 — Won't Run — 12 modules

Compiles fine. Fails at runtime on specific code paths.

| Module | What breaks |
|--------|------------|
| `jackson-dates-timestamps` | `spring.jackson.serialization.write-dates-as-timestamps=true` no longer binds — one leftover config line stops the app starting |
| `cors-empty-config-not-rejected` | Preflight against an empty CORS config: 403 on 3.5, 200 on 4.0 — requests that used to be blocked get through |
| `javax-annotation-removed` | `@javax.annotation.PostConstruct` compiles but Spring silently ignores it — init code never runs |
| `javax-inject-removed` | `@javax.inject.Named` beans no longer registered — `UnsatisfiedDependencyException` at context load |
| `jackson-exception-hierarchy` | `JacksonException` no longer extends `IOException` — catch blocks go dead |
| `batch-schema-change` | Spring Batch 6 renames metadata sequences — `ClassNotFoundException` / DDL migration required |
| `batch-in-memory-default` | Spring Batch 6 defaults to in-memory job repository — JDBC metadata tables silently absent |
| `health-probes-default-on` | Liveness/readiness probe groups enabled by default — new endpoints appear |
| `httpmessageconverters-deprecated` | `HttpMessageConverters` gone at runtime — `NoClassDefFoundError` |
| `pkce-mandatory` | PKCE enforced for all OAuth 2.0 clients — authorization requests change shape |

### Tier 3 — Different Results — 7 modules

Compiles, starts, runs, passes your existing tests. Produces different output.

| Module | What breaks |
|--------|------------|
| `mongodb-property-renames` | `spring.data.mongodb.*` ignored on 4.0 — the app connects to `localhost:27017/test` instead of your configured database |
| `jackson-date-serialisation` | Dates flip from `1699257000000` to `"2023-11-06T05:30:00Z"` |
| `jackson-locale-format` | `Locale.US` serialises as `en-US` instead of `en_US` — breaks caching, i18n |
| `hibernate-native-datetime` | Native queries return `java.time.LocalDate` instead of `java.sql.Date` — silent type change |

## How it works

The parent POM imports the Spring Boot BOM as a dependency (not as a parent), which means the version is a property you can override from the command line:

```xml
<properties>
    <spring-boot.version>3.5.16</spring-boot.version>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>${spring-boot.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

```bash
mvn test -Dspring-boot.version=4.0.7
```

This is also how most enterprise projects consume Spring Boot (via BOM, not parent), so the test structure mirrors real-world builds.

## Related

These test cases accompany the *"Won't Launch, Won't Run, Wrong Results"* article series on migrating from Spring Boot 3.5 to 4.0.
