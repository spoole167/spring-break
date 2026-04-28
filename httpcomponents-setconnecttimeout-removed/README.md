# RestTemplateBuilder.setConnectTimeout Removed (Tier 1: Won't Compile)

**Summary**: The deprecated `setConnectTimeout(Duration)` and `setReadTimeout(Duration)` methods in `RestTemplateBuilder` have been removed in Spring Boot 4.0. They have been replaced by `connectTimeout(Duration)` and `readTimeout(Duration)`.

## What breaks

In Spring Boot 3.5, `RestTemplateBuilder` provides `setConnectTimeout` and `setReadTimeout` methods to configure timeouts for the underlying client. These methods were deprecated in 3.4.

In Spring Boot 4.0, these methods are removed. Code that calls them will fail to compile.

```java
// Spring Boot 3.5 (Works)
public RestTemplate restTemplate(RestTemplateBuilder builder) {
    return builder
        .setConnectTimeout(Duration.ofSeconds(5))
        .setReadTimeout(Duration.ofSeconds(5))
        .build();
}

// Spring Boot 4.0 (Compilation Error)
// cannot find symbol: method setConnectTimeout(java.time.Duration)
```

## How this test works

The module `httpcomponents-setconnecttimeout-removed` contains:
- `RestTemplateTimeoutUsage.java`: A class that calls `builder.setConnectTimeout(Duration)`.
- `RestTemplateTimeoutTest.java`: A test that asserts the method works and is discoverable via reflection.

On Boot 3.5: Compiles and passes.
On Boot 4.0: Fails to compile with a "cannot find symbol" error for `setConnectTimeout`.

## Fix / Migration Path

Rename `setConnectTimeout(Duration)` to `connectTimeout(Duration)` and `setReadTimeout(Duration)` to `readTimeout(Duration)`.

```java
// Spring Boot 4.0 (Fixed)
public RestTemplate restTemplate(RestTemplateBuilder builder) {
    return builder
        .connectTimeout(Duration.ofSeconds(5))
        .readTimeout(Duration.ofSeconds(5))
        .build();
}
```

## References

- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- Master list entry: 1.34
