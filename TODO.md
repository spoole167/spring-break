# Test Cases Runbook — Adding Tier 1 / Tier 2 Modules

**Purpose:** Self-contained instructions for an LLM agent to mechanically extend the Spring Boot 3.5 → 4.0 test-cases suite with new Tier 1 (Won't Compile / Won't Resolve) and Tier 2 (Won't Run) modules.

**Use:** Read this runbook in full before doing any work. Pick one item from the priority backlog at the end. Follow the recipe end-to-end. Verify. Update docs. Move on.

**Hard rule, no exceptions:** every claim a new module makes must be backed by a verbatim quote from one of the six primary sources listed below. If you can't find a source quote, stop and flag it — do not fabricate.

---

## Section 1 — Background context



**Key reference documents (read these first):**

- `01-Projects/SpringBoot Promotion/Research/Boot 4.0 Breaking Changes - Master List.md` (Obsidian) — the canonical enumeration of 143 distinct breaking changes with verbatim source quotes. Each numbered entry (1.1, 2.7, 3.14, etc.) is the unit of work.
- `01-Projects/SpringBoot Promotion/Research/Verification Status - Test Cases Suite.md` (Obsidian) — truth table tracking which modules are fully verified.
- `test-cases-todo.md` (project folder) — backlog of work items.
- `test-cases-audit.md` (project folder) — historical audit record.

**Six primary sources:**

1. Boot 4.0 Migration Guide — `https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide`
2. Boot 4.0 Release Notes — `https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes`
3. Spring Framework 7.0 Release Notes — `https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Release-Notes`
4. Hibernate 7 Migration Guide — `https://docs.hibernate.org/orm/7.0/migration-guide/migration-guide.html`
5. Jackson 3 Migration Guide — `https://github.com/FasterXML/jackson/blob/main/jackson3/MIGRATING_TO_JACKSON_3.md`
6. Spring Security 7 Migration — `https://docs.spring.io/spring-security/reference/6.5/migration-7/{configuration,oauth2,saml2,ldap,messaging,web,authentication,authorization}.html` and `https://docs.spring.io/spring-security/reference/7.0/migration/servlet/{index,oauth2,authorization,saml2}.html`
7. Spring Batch 6.0 Migration Guide — `https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide`

**Test versions:**

- Default (passes): Spring Boot **3.5.14**
- Override (fails): Spring Boot **4.0.6**
- Versions controlled by `<spring-boot.version>` property in `test-cases/pom.xml`

---

## Section 2 — Suite conventions (must follow)

### Folder layout per module

```
test-cases/<module-name>/
├── pom.xml
├── README.md
└── src/
    ├── main/
    │   ├── java/com/example/<...>.java
    │   └── resources/
    │       └── application.properties      # only when needed
    └── test/
        └── java/com/example/<TestName>Test.java
```

### Naming conventions

- **Module folder name:** lowercase, hyphenated, descriptive of the issue (`testrest-template-removed`, not `m11-test-rest-removed`).
- **Java package:** always `com.example`.
- **Application class:** `<SomethingApp>` (e.g. `JacksonInclusionApp`) — required if the module uses `@SpringBootTest`.
- **Test class:** Single test class named `<DescriptiveName>Test`. Use JUnit 5 (`@Test` from `org.junit.jupiter.api.Test`).

### pom.xml template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.example</groupId>
        <artifactId>spring-boot-migration-tests</artifactId>
        <version>1.0.0</version>
    </parent>

    <artifactId><module-name></artifactId>
    <name>Tier <N> — <Short headline></name>
    <description><One-sentence description of the breaking change></description>

    <dependencies>
        <!-- module-specific deps. Use Boot starters where possible. -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

</project>
```

Do **not** declare a Spring Boot version in module poms. The version comes from the parent's `<spring-boot.version>` property, which is overridden via `-Dspring-boot.version=4.0.6` for the failing run.

### README.md template (every module needs one)

```markdown
# <Headline> (Tier <N>: <Won't Compile|Won't Run|Wrong Results>)

**Summary**: <one-paragraph plain-language explanation of the breaking change>

## What breaks

<2-4 paragraphs describing what works on 3.5 and breaks on 4.0, with code examples>

## How this test works

<which Java files are in the module, what each does, what the test asserts>

On Boot 3.5: <expected outcome>.
On Boot 4.0: <expected outcome>.

## Fix / Migration Path

<the actual migration step. Code before/after where helpful.>

## References

- [<Source name>](<URL>) — anchor `<section-heading>`
- Master list entry: <e.g. 1.13>
```

---

## Section 3 — Recipe for a Tier 1 (Won't Compile / Won't Resolve) module

Tier 1 means the build fails on 4.0 *before* tests run. Three sub-patterns.

### Pattern T1A: Class no longer exists

The pre-4.0 class is removed. Code that imports it fails to compile.

**Files to create:**

`src/main/java/com/example/<App>.java`:
```java
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class <App> {
    public static void main(String[] args) {
        SpringApplication.run(<App>.class, args);
    }
}
```

`src/main/java/com/example/<UsageDemo>.java`:
```java
package com.example;

import <fully.qualified.removed.Class>;     // <-- the import that breaks on 4.0

public class <UsageDemo> {
    public static <ReturnType> demonstrate() {
        return new <RemovedClass>(...);     // direct usage of the removed class
    }
}
```

`src/test/java/com/example/<DescriptiveName>Test.java`:
```java
package com.example;

import org.junit.jupiter.api.Test;
import <fully.qualified.removed.Class>;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

class <DescriptiveName>Test {

    @Test
    void <removedClass>ShouldExistOnBoot35() {
        // Direct use — fails to compile on Boot 4.0.
        <ReturnType> instance = <UsageDemo>.demonstrate();
        assertNotNull(instance);
    }

    @Test
    void <removedClass>IsLoadableViaReflection() {
        // Belt-and-braces: even if the import resolves, ensure the class loads at runtime.
        assertDoesNotThrow(
            () -> Class.forName("<fully.qualified.removed.Class>"),
            "<RemovedClass> should be on classpath on Boot 3.5. Removed in 4.0."
        );
    }
}
```

### Pattern T1B: Artifact no longer in BOM

The starter or jar is dropped from the Spring Boot dependency-management. Module pom declares it without version.

**Pom adjustment:**
```xml
<!-- This dep relies on Boot's BOM to provide the version.
     On 4.0 the BOM no longer manages it → "version is missing" error.
     Do NOT pin a version. -->
<dependency>
    <groupId><groupId-of-removed-artifact></groupId>
    <artifactId><artifactId-of-removed-artifact></artifactId>
</dependency>
```

**Source class:** A minimal usage that's compile-clean on 3.5. The pom failure happens before compile on 4.0, so the source is for 3.5 verification only.

**Test class:** Reflection check that asserts the class exists on classpath. Pattern same as T1A second test.

### Pattern T1C: Method/method-signature removed

A method on a still-existing class is removed. Code that calls it fails to compile.

**Source class:** Calls the removed method directly:
```java
package com.example;
import <package.with.class>;

public class <UsageDemo> {
    public static void useRemovedMethod() {
        <Class> instance = ...;
        instance.<removedMethod>(...);   // <-- compile fails on 4.0
    }
}
```

**Test class:** Calls `useRemovedMethod()` and asserts it doesn't throw. On 3.5 it compiles + runs. On 4.0 it doesn't compile.

### Notes for all Tier 1 patterns

- **Two assertions per test** when feasible: direct usage (catches compile-time breaks) AND reflection (catches runtime classpath breaks). Some breaks only show up at one level, not both.
- **Do not use `@Disabled` or wrap in try/catch to make tests pass on 4.0.** The test is supposed to fail on 4.0. That's the demonstration.
- Add a Javadoc on the test class quoting the master-list entry briefly: `/* Master list: 1.40 — TestRestTemplate package relocated. */`

---

## Section 4 — Recipe for a Tier 2 (Won't Run) module

Tier 2 means the build compiles on both 3.5 and 4.0, but at runtime the 4.0 application fails — startup error, missing bean, exception, wrong result type. Two sub-patterns.

### Pattern T2A: Bean no longer auto-configured

A bean that Spring used to auto-configure is no longer provided. Code that injects it gets `NoSuchBeanDefinitionException` at startup.

**Files:**

`src/main/java/com/example/<App>.java`: standard `@SpringBootApplication`.

`src/main/java/com/example/<Service>.java`:
```java
package com.example;

import org.springframework.beans.factory.annotation.Autowired;
import <package.of.formerly.autoconfigured.Bean>;
import org.springframework.stereotype.Component;

@Component
public class <Service> {
    @Autowired
    private <FormerlyAutoConfiguredBean> bean;

    public <FormerlyAutoConfiguredBean> getBean() {
        return bean;
    }
}
```

`src/test/java/com/example/<Name>Test.java`:
```java
package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.assertNotNull;

@SpringBootTest
class <Name>Test {

    @Autowired
    private <Service> service;

    @Test
    void formerlyAutoConfiguredBeanShouldBeInjected() {
        assertNotNull(service.getBean(),
            "<BeanType> was auto-configured on Boot 3.5. " +
            "Removed in 4.0 — application fails to start.");
    }
}
```

### Pattern T2B: Behaviour change at runtime

The class still exists and the build succeeds, but a method now returns a different type, the default config flag flipped, or a check that previously passed now throws.

**Source class:** Exercises the API that changed.

**Test class:** Asserts the pre-4.0 behaviour. On 4.0 the assertion fails.

```java
@Test
void apiBehaviourMatchesBoot35() {
    <ReturnType> result = <Service>.exerciseChangedAPI();
    assertEquals(<expectedOn35>, result,
        "<API> returned <X> on Boot 3.5. " +
        "On 4.0 it returns <Y> — silent breaking change.");
}
```

### Notes for Tier 2 patterns

- Use `@SpringBootTest` for context-loading tests. `@SpringBootTest(webEnvironment = RANDOM_PORT)` is fine but **don't depend on `TestRestTemplate`** — that class was removed in Boot 4.0. Use `org.springframework.web.client.RestClient` (Spring Framework, available on both versions) with `@LocalServerPort`.
- For runtime exception assertions: use `assertThrows(<ExpectedException>.class, () -> ...)` with the expected pre-4.0 type. On 4.0 a different exception will fly past `assertThrows` and fail the test.
- Avoid timing/ordering-dependent tests. They're flaky and don't make good demos.

---

## Section 5 — Mandatory verification (do not skip)

After creating any new module, run **both** sweeps before marking the module done:

### 5.1 Confirm 3.5 passes

```bash
cd test-cases
mvn -B -ntp -pl <module-name> test
```

Expected outcome: `BUILD SUCCESS` with `Tests run: N, Failures: 0, Errors: 0`.

If the test fails on 3.5, the test is wrong. Fix it before continuing.

### 5.2 Confirm 4.0 fails for the right reason

```bash
cd test-cases
mvn -B -ntp -pl <module-name> test -Dspring-boot.version=4.0.6
```

Expected outcome depends on tier:

- **Tier 1A/C:** `BUILD FAILURE` at `compile` or `testCompile` phase, with a `cannot find symbol` or `package does not exist` error mentioning the specific class/package the README claims is gone.
- **Tier 1B:** `BUILD FAILURE` at the `validate` phase with `'dependencies.dependency.version' for <groupId>:<artifactId>:jar is missing`.
- **Tier 2A:** `BUILD FAILURE` at `test` with `UnsatisfiedDependencyException` / `NoSuchBeanDefinitionException` referencing the bean type the README claims is no longer auto-configured.
- **Tier 2B:** `BUILD FAILURE` at `test` with an `AssertionFailedError` whose message describes the behaviour change.

**Critical:** if the test passes on 4.0, the module is wrong. Either:

- The change isn't real on 4.0.6 (the master-list claim is wrong — flag it, do not commit the module).
- The test isn't exercising the change (rewrite the test).

Three modules have already been deleted from the suite for failing this check (`auth-default-deny`, plus the original framings of `path-matching-engine` and `jackson-property-inclusion`). Do not repeat those mistakes.

### 5.3 Confirm the failure message matches the README claim

Read the actual error output. The error must mention the specific class, method, package, or behaviour the README headline describes.

If the README headline says "AntPathRequestMatcher removed" but the error is "spring-boot-starter-aop:jar version is missing", the test is failing for an unrelated reason. Stop. Either fix the test scenario or pick a different demo.

---

## Section 6 — Documentation updates required after each module

Once a module is verified, update **all** of the following:

### 6.1 Parent pom (`test-cases/pom.xml`)

Add `<module><module-name></module>` to the appropriate category block. Update the count comment at the top of the `<modules>` section. Update the count in the Category-(a/c/d) block comments.

```xml
<!-- 32 modules organised by migration failure mode.
     Run on 3.5.14: all pass.  Run on 4.0.6: all fail. -->
<modules>
    <!-- Category (a) — Won't Compile / Won't Resolve on 4.0  (18 modules) -->
    ...
    <module><module-name></module>
    ...
</modules>
```

### 6.2 Test runner (`test-cases/run-all-tests.sh`)

Add the module name to `CATEGORY_A=()` (Tier 1) or `CATEGORY_C=()` (Tier 2) in the array.

### 6.3 Master list (Obsidian)

`01-Projects/SpringBoot Promotion/Research/Boot 4.0 Breaking Changes - Master List.md`:

Find the entry corresponding to the new module (e.g. 1.40 if you built `testrest-template-removed`). Change the `Existing module:` line from `GAP` to the new module name.

### 6.4 Verification status (Obsidian)

`01-Projects/SpringBoot Promotion/Research/Verification Status - Test Cases Suite.md`:

Add a row to **Section A1 (VERIFIED)** for the new module. Decrement the count in **Section B (DOC-ONLY)** if the change you covered was previously listed there.

### 6.5 TODO file (Obsidian + project folder)

`01-Projects/SpringBoot Promotion/Research/Test Cases TODO.md` and `test-cases-todo.md`:

Mark the corresponding TODO item `[x]` (done).

---

## Section 7 — Quality controls

### 7.1 Anti-patterns — do NOT do these

- **Do not invent a class, method, package, or annotation that you can't find a verbatim source quote for.** This is the single biggest risk to the suite's credibility. If the master list says `Class X was removed` but you can't find that class in any of the six primary sources, the master list might be wrong — flag it, do not build a module.
- **Do not pin a Spring Boot version in a module pom.** The parent's `<spring-boot.version>` property must control it.
- **Do not use `TestRestTemplate`.** It's removed in Boot 4.0. Use `RestClient` + `@LocalServerPort` if you need an HTTP client in a test.
- **Do not depend on `MockMvc` auto-configuration.** `@SpringBootTest` no longer auto-configures `MockMvc` on 4.0. If you need MockMvc, add `@AutoConfigureMockMvc` explicitly — but be aware this will pull in additional Boot test deps that may not exist.
- **Do not skip Section 5 verification.** Both sweeps must pass.
- **Do not write a test that asserts `assertTrue(true)` or similar tautologies.** The test must actually exercise the change.
- **Do not silently delete or move existing modules** without an explicit instruction in the master list or TODO.

### 7.2 If you can't make a module work, document why and stop

Some master-list entries can't be turned into a Maven test:

- Anything requiring **GraalVM native-image** build (1.1 partly, 2.15, 2.16, 1.71)
- Anything requiring **Gradle** (1.1 partly, M36)
- Anything requiring **Kotlin** (1.1 partly, M2)
- Anything requiring a **specific external database** (Hibernate Oracle DDL changes — 3.18, 3.19, partial 3.20, 3.21)
- Anything requiring **war deployment to a real Tomcat** (M22, 2.1)

For these, do **not** stub a fake test. Add a note to the TODO file explaining why the item isn't testable in this suite.

---

## Section 8 — Priority backlog

Build these in order. Each line: master-list-entry · suggested module name · pattern · expected effort.

### Tier 1 — Won't Compile / Won't Resolve

| ML # | Suggested module name | Pattern | Notes |
|---|---|---|---|
| 1.13 | `bootstrap-registry-relocated` | T1A | [x] `BootstrapRegistry` and `EnvironmentPostProcessor` package move |
| 1.40 | `testrest-template-removed` | T1A | [x] `TestRestTemplate` removed from `org.springframework.boot.test.web.client`. High-impact for migrating teams. |
| 1.39 | `mockito-test-execution-listener` | T2A | [x] `@Mock` / `@Captor` need `MockitoExtension` |
| 1.36 | `httpheaders-multivaluemap` | T1C | [x] `HttpHeaders` no longer extends `MultiValueMap` |
| 1.30 | `javax-annotation-removed` | T1A | [x] `javax.inject.Inject` / `javax.annotation.PostConstruct` no longer supported |
| 1.46 | `elasticsearch-rest5client` | T1A | [x] `RestClient` → `Rest5Client` rename |
| 1.47 | `entityscan-relocated` | T1A | [x] `@EntityScan` package moved to `org.springframework.boot.persistence.autoconfigure` |
| 1.43 | `propertymapping-relocated` | T1A | [x] `@PropertyMapping` annotation moved |
| 1.44 | `kafka-streams-customizer-removed` | T1A | [x] `StreamBuilderFactoryBeanCustomizer` → `StreamsBuilderFactoryBeanConfigurer` |
| 1.32 | `webjars-locator-core-removed` | T1B | [!] `webjars-locator-core` → `webjars-locator-lite` — no mention in Boot 4.0 Migration Guide or Release Notes; master list claim lacks primary source. Do not build until a verbatim source quote is found. |
| 1.59 | `simpdest-message-matcher-removed` | T1A | [x] Spring Security messaging matcher removed |
| 1.60 | `apacheds-ldap-removed` | T1B | [x] ApacheDS embedded LDAP support removed; use UnboundId |
| 1.62 | `spring-security-access-relocated` | T1B | [x] Access API moved to legacy `spring-security-access` module |
| 1.14 | `propertymapper-alwaysapplyingnonnull` | T1C | [x] `PropertyMapper.alwaysApplyingWhenNonNull()` removed |
| 1.34 | `httpcomponents-setconnecttimeout-removed` | T1C | [x] `setConnectTimeout` method removed |
| 1.52 | `hibernate-query-setorder-removed` | T1C | [x] `Query#setOrder` removed |
| 1.53 | `hibernate-empty-interceptor-removed` | T1A | [x] `EmptyInterceptor` removed |
| 1.51 | `hibernate-where-orderby-removed` | T1A | [x] Subset of removed Hibernate annotations: pick `@Where` and `@OrderBy` for the test (combined module) |
| 1.68 | `batch-job-builder-string-constructor` | T1C | [x] `JobBuilder(String)` constructor removed |
| 1.67 | `batch-package-moves` | T1A | [x] `org.springframework.batch.core.*` package relocations (`Job`, `JobExecution`, etc.) |
| 1.69 | `batch-chunkhandler-renamed` | T1C | [x] `ChunkHandler` → `ChunkRequestHandler`; `setJobLauncher` → `setJobOperator` |
| 1.70 | `actuator-nullable-removed` | T1A | [x] Actuator endpoint params can no longer use `org.springframework.lang.Nullable` |
| 1.10 | `aop-starter-rename` | T1B | [x] `spring-boot-starter-aop` → `spring-boot-starter-aspectj` |

### Tier 2 — Won't Run

| ML # | Suggested module name | Pattern | Notes |
|---|---|---|---|
| 1.41 | `springboottest-no-mockmvc` | T2A | `@SpringBootTest` no longer auto-configures `MockMvc`; inject fails without `@AutoConfigureMockMvc` |
| 2.6 | `batch-in-memory-default` | T2A | Spring Batch defaults to in-memory; need `spring-boot-starter-batch-jdbc` for old behaviour. High-impact silent change. |
| 2.2 | `health-probes-default-on` | T2B | Liveness/readiness probes enabled by default; new health groups appear |
| 2.3 | `httpmessageconverters-deprecated` | T2A | Custom converter beans no longer accepted |
| 2.5 | `jersey-jackson2-required` | T2A | Jersey 4.0 doesn't support Jackson 3 |
| 2.9 | `batch-static-meterregistry-removed` | T2A | Must register `ObservationRegistry` bean |
| 2.14 | `springextension-method-scope` | T2B | `@Nested` / custom `TestExecutionListener` impacted |
| 2.17 | `cors-empty-config-not-rejected` | T2B | CORS pre-flight no longer rejected when CORS config empty |
| 2.18 | `webclient-system-proxy-optin` | T2B | Reactor `WebClient` auto-opts into `https.proxyHost`/`https.proxyPort` |
| 2.32 | `jackson-find-and-add-modules` | T2B | All classpath modules registered by default |
| 2.33 | `logback-utf8-default` | T2B | Default Charset for log files now UTF-8 |
| 2.34 | `devtools-livereload-disabled` | T2B | LiveReload off by default |
| 2.37 | `sanitizabledata-null-key` | T2B | `SanitizableData` throws on `null` key |
| 2.36 | `autoconfiguration-public-members` | T2B | Public members removed from auto-config classes |
| 2.11 | `sec7-opaquetoken-credentials-encoded` | T2B | Authorization header now built differently |
| 2.13 | `sec7-loginurl-relative-redirect` | T2B | `LoginUrlAuthenticationEntryPoint` defaults to relative URI |
| 2.31 | `hibernate-scan-jandex-required` | T2A | Entity discovery needs `hibernate-scan-jandex` module |
| 2.27 | `hibernate-immutable-update-throws` | T2B | Update/delete on immutable entities now throws |
| 2.25 | `hibernate-detached-refresh-throws` | T2B | Refreshing detached entity now throws `IllegalArgumentException` |
| 2.30 | `hibernate-jndi-autobind` | T2B | `SessionFactory` auto-binds to JNDI when name set |

### How to use this backlog

1. Pick one item.
2. Read the master-list entry for it (Boot 4.0 Breaking Changes - Master List.md, find entry by number).
3. Determine the right pattern from Section 3 / Section 4.
4. Build the module per the templates.
5. Run Section 5 verification.
6. Update Section 6 docs.
7. Move to next item.

If you finish a row in this backlog and want more, look at the master list for any entry where `Existing module: GAP`.

---

## Section 9 — Worked example

The fastest way to internalise the recipe is to look at a recently rebuilt module:

`test-cases/path-matching-engine/` was rebuilt as a Tier 1 demo of master-list entry **1.58** (`AntPathRequestMatcher` removed in Spring Security 7.0). It contains:

- `pom.xml` — declares `spring-boot-starter-web` + `spring-boot-starter-security` + `spring-boot-starter-test`. No Boot version pinned.
- `src/main/java/com/example/PathMatchingApp.java` — standard `@SpringBootApplication`.
- `src/main/java/com/example/SecurityConfig.java` — imports `AntPathRequestMatcher`, uses it in a `SecurityFilterChain` bean.
- `src/test/java/com/example/PathMatchingEngineTest.java` — direct usage assertion + reflection check.
- `README.md` — full template format.

Read those files before building your first module. The shape of `path-matching-engine` is the shape of every Tier 1A module.

For a Tier 2A example: `test-cases/resttemplate-autoconfig/` (covers entry 1.40 from a runtime-injection angle).
For a Tier 1B example: `test-cases/spring-retry-removed/` (covers entry 1.15 with no version pin).
For a Tier 1C example: `test-cases/hibernate-session-delete/` (covers entry 1.49 — method removal).

---

## Section 10 — Final reporting

After building one or more modules, report back with:

1. **Module name(s) created**
2. **Master-list entry number(s)** that each module covers
3. **Verification log:** copy the last 5–10 lines of each `mvn test` (3.5) and `mvn test -Dspring-boot.version=4.0.6` output, showing the test outcomes.
4. **Documentation updates applied:** confirm parent pom, run-all-tests.sh, master list, verification status, and TODO have all been updated.
5. **Any items skipped or flagged:** if a master-list claim couldn't be reproduced on 4.0.6, record the entry number and the unexpected outcome — do **not** force a fake demo.

That's the runbook. Pick a row from Section 8 and go.
