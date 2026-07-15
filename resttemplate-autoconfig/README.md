# RestTemplateBuilder relocated (Tier 1: Won't Compile)

**Summary**: Spring Boot 4.0 breaks the monolithic `spring-boot` jar into per-technology modules, and `RestTemplateBuilder` moves out of its long-standing home at `org.springframework.boot.web.client` as part of that reshuffle. Any class that injects the builder, which is the pattern the Boot team recommended for years as the right way to get a `RestTemplate`, fails to compile on Boot 4.0 because the import no longer resolves.

## What breaks

In Spring Boot 3.5, the standard recommended pattern compiles and works:

```java
import org.springframework.boot.web.client.RestTemplateBuilder;

@Service
public class ApiClient {

    private final RestTemplate restTemplate;

    public ApiClient(RestTemplateBuilder builder) {
        this.restTemplate = builder.build();
    }
}
```

In Spring Boot 4.0, the package is gone:

```
[ERROR] package org.springframework.boot.web.client does not exist
```

## How this test works

`RestTemplateApp` is a minimal `@SpringBootApplication`. `ApiClient` is a `@Service` whose constructor takes the auto-configured `RestTemplateBuilder` and calls `builder.build()` to create its `RestTemplate`. `RestTemplateAutoConfigTest` is a `@SpringBootTest` that autowires `ApiClient`; its single test, `restTemplateShouldBeAutoConfigured()`, asserts `apiClient.getRestTemplate()` is non-null, proving the builder was provided by auto-configuration and the wiring worked end to end.

- On Boot 3.5.16: compiles and passes.
- On Boot 4.0.7: fails at compile with `package org.springframework.boot.web.client does not exist` (`RestTemplateBuilder` relocated in Boot 4). Verified 15 July 2026.

## Fix / Migration Path

Two options, in increasing order of ambition:

1. Update the import to `RestTemplateBuilder`'s relocated package in Boot 4 and make sure the corresponding Boot module (the split-out HTTP client starter) is on your classpath. The injection pattern itself still works; only the coordinates changed.
2. Take the migration as the prompt to move to `RestClient`, Spring's fluent successor to `RestTemplate`, via the auto-configured `RestClient.Builder`. `RestClient` is available on Boot 3.5 today, so the rewrite can happen before the upgrade rather than during it.

Either way, expect this break to show up in every service class that touches HTTP: builder injection was the officially recommended pattern, so it is everywhere.
