# HttpComponents request factory setConnectTimeout(int) removed (Tier 1: Won't Compile)

**Summary**: The `int`-based timeout setters on `HttpComponentsClientHttpRequestFactory` — `setConnectTimeout(int)` and `setConnectionRequestTimeout(int)` — were deprecated in Spring Framework 6.1 and are removed in Spring Framework 7.0 (Spring Boot 4.0). Code that configures timeouts with raw milliseconds no longer compiles.

## What breaks

In Spring Boot 3.5 (Framework 6.2), configuring an HttpComponents-backed `RestTemplate` with millisecond timeouts compiles (with deprecation warnings):

```java
HttpComponentsClientHttpRequestFactory factory = new HttpComponentsClientHttpRequestFactory();
factory.setConnectTimeout(5000);
factory.setConnectionRequestTimeout(5000);
```

In Spring Boot 4.0 (Framework 7.0), the deprecated `int` variants are gone:

```
[ERROR] cannot find symbol
  symbol:   method setConnectTimeout(int)
  location: variable factory of type org.springframework.http.client.HttpComponentsClientHttpRequestFactory
```

## How this test works

`HttpComponentsUsage.configureTimeout()` calls both `int` setters. `HttpComponentsTimeoutTest` asserts the factory is created.

- On Boot 3.5.16: compiles and passes.
- On Boot 4.0.7: fails at compile — `cannot find symbol: method setConnectTimeout(int)`. Verified 15 July 2026.

## Fix / Migration Path

Switch to the `Duration` variants, available since Framework 6.1 — so this can be done on 3.5 before migrating:

```java
factory.setConnectTimeout(Duration.ofSeconds(5));
factory.setConnectionRequestTimeout(Duration.ofSeconds(5));
```

Or configure timeouts via `ClientHttpRequestFactorySettings` / `RestTemplateBuilder` instead of touching the factory directly.

## Source

Spring Framework 7.0 Release Notes ("Removed APIs" section):

> The `HttpComponentsClientHttpRequestFactory#setConnectTimeout` methods have been removed as part of [#35748](https://github.com/spring-projects/spring-framework/issues/35748).

https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Release-Notes
