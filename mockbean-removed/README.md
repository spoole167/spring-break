# @MockBean and @SpyBean Removed (Tier 1: Won't Compile)

@MockBean and @SpyBean annotations removed; use @MockitoBean and @MockitoSpyBean instead.

## What Breaks

Spring Boot 4.0 removes the `@MockBean` and `@SpyBean` annotations from `org.springframework.boot.test.mock.mockito`. The whole package is gone, so any test that imports them stops compiling. This is a build failure, not a runtime failure: with a clean build against 4.0 you never get as far as running a test.

**Measured on Spring Boot 4.0.7 (clean build):**
```
[ERROR] ServiceTest.java: package org.springframework.boot.test.mock.mockito does not exist
```

The `mvn clean test` run fails at the test-compile phase. The replacements are Spring Framework's native bean override annotations: `@MockitoBean` and `@MockitoSpyBean` in `org.springframework.test.context.bean.override.mockito`.

## Trap: Why This Gets Misdiagnosed as a Runtime Problem

If you switch a project to 4.0 and run tests without a clean build, stale test classes compiled against 3.5 are still sitting in `target/test-classes`. Those classes load and run, but Spring no longer recognises the old annotations, so the mock and spy fields silently stay `null`. The first symptom is a `NullPointerException` deep inside a test, which looks like a runtime injection failure. It is not. Run `mvn clean test` and the real story appears: the code never compiled against 4.0 in the first place.

## How This Test Works

The test demonstrates the use of both `@MockBean` (full mock) and `@SpyBean` (partial mock/spy) in a Spring Boot test:

- **ServiceTest.testMockBean()**: Uses `@MockBean` to completely replace MyService with a mock. The test stubs behaviour using `when()` and verifies method calls with `verify()`.
- **ServiceTest.testSpyBean()**: Uses `@SpyBean` on HelperService to wrap the real bean. Real methods execute unless explicitly stubbed; `verify()` confirms the real methods were called.

The supporting beans (MyService, HelperService) are simple Spring-managed services. The test runs in a `@SpringBootTest` context, which on 3.5.16 correctly injects the mocked and spied beans. On 4.0.7 the test sources fail to compile because the annotation package no longer exists.

Verified 15 July 2026.

## On Spring Boot 3.5.16

```bash
mvn clean test
```

Output:
```
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
```

Both tests pass because `@MockBean` and `@SpyBean` are available in `spring-boot-test`.

## On Spring Boot 4.0.7

Compilation of the test sources fails:
```
[ERROR] package org.springframework.boot.test.mock.mockito does not exist
```

No tests run.

## Fix / Migration Path

Replace all occurrences of the old annotations with their new equivalents:

**1. Update imports:**
```java
// Remove these
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.boot.test.mock.mockito.SpyBean;

// Add these
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.context.bean.override.mockito.MockitoSpyBean;
```

**2. Replace annotations:**
```java
// @MockBean → @MockitoBean
@MockitoBean
private MyService mockService;

// @SpyBean → @MockitoSpyBean
@MockitoSpyBean
private HelperService spyHelper;
```

**3. Verify pom.xml:**
Ensure `spring-boot-starter-test` is included (brings Mockito and Spring test context bean override support). No additional dependencies required.

**4. Test behaviour:**
Run `mvn clean test` to confirm mocks and spies work as expected. The Mockito-native approach may be stricter about stub matching; if needed, use `Mockito.lenient()` to relax matching rules.

## References

- Spring Boot 4.0 Migration Guide (Testing section): https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
- Spring Boot 4.0 Bean Override: https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes
- Mockito Documentation: https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html
