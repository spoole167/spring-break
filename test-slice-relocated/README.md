# Test-slice annotations relocated (Tier 1: Won't Compile)

**Summary**: Spring Boot 4.0 splits the monolithic test-autoconfigure jar along technology lines, and the test-slice annotations move with it. `@DataJpaTest` no longer lives at `org.springframework.boot.test.autoconfigure.orm.jpa`; each slice annotation now belongs to its technology's own test module. Every sliced test in your suite, and most non-trivial Spring codebases have hundreds, fails to compile on Boot 4.0 because the import path is gone.

## What breaks

In Spring Boot 3.5, the classic JPA slice test compiles and runs:

```java
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

@DataJpaTest
class TestSliceRelocatedTest {
    @Autowired
    private UserRepository userRepository;
    ...
}
```

In Spring Boot 4.0, the package no longer exists:

```
[ERROR] package org.springframework.boot.test.autoconfigure.orm.jpa does not exist
```

## How this test works

`TestSliceApp` is a minimal `@SpringBootApplication`; `User` is a JPA `@Entity` mapped to the `users` table, and `UserRepository` extends `JpaRepository<User, Long>`. The test tree also carries `TestAutoConfig`, a small `@Configuration` producing a marker bean. `TestSliceRelocatedTest` is annotated `@DataJpaTest` with a `@TestPropertySource` setting `spring.jpa.hibernate.ddl-auto=create-drop`, and runs two tests against H2: `dataJpaTestSliceShouldAutoConfigureRepository()` saves a `User`, reads it back by ID and checks the fields, proving the whole JPA slice (H2, entity manager, repository) was auto-configured; `entityManagerFactoryShouldBePresent()` asserts the context contains an `entityManagerFactory` bean.

- On Boot 3.5.16: compiles and passes.
- On Boot 4.0.7: fails at compile with `package org.springframework.boot.test.autoconfigure.orm.jpa does not exist` (test-slice annotations moved to per-technology modules in Boot 4). Verified 15 July 2026.

## Fix / Migration Path

Update each slice annotation's import to its relocated package in Boot 4 and make sure the matching per-technology test artifact is on your test classpath; `spring-boot-starter-test` alone no longer carries every slice. The annotations keep their names and semantics, so this is mechanical, but it is mechanical across your entire test suite at once: `@DataJpaTest`, `@WebMvcTest`, `@JsonTest` and the rest all moved. Budget for a bulk import rewrite (or an OpenRewrite recipe) rather than fixing files as they fail.
