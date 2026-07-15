# CORS Empty Configuration Not Rejected (Tier 2: Won't Run)

**Summary**: Spring Framework 7.0 (Spring Boot 4.0) changes how CORS pre-flight requests are handled when an "empty" `CorsConfiguration` is registered. Requests that 3.5 blocked with a 403 now get through with a 200.

## What breaks

In Spring Framework 6.x (Spring Boot 3.5), registering a `CorsConfiguration` with no allowed origins, methods or headers gives you fail-closed behaviour: `DefaultCorsProcessor` rejects CORS pre-flight (`OPTIONS`) requests with `403 Forbidden` because nothing matches.

In Spring Framework 7.0 the same registration no longer rejects the pre-flight. The measured result is a straight `403 -> 200` flip: a request that was blocked on 3.5 succeeds on 4.0. Any application that relied on an empty CORS config as a default-deny gate has silently opened up. Nothing fails at build time and nothing fails at startup; the security posture just changes.

```java
// Registered via CorsFilter or WebMvcConfigurer
source.registerCorsConfiguration("/**", new CorsConfiguration());
```

## How this test works

The module `cors-empty-config-not-rejected` contains:
- `CorsApp.java`: Registers a `CorsFilter` with an empty `CorsConfiguration` for `/**`, plus a trivial `/hello` endpoint.
- `CorsPreflightTest.java`: Sends an `OPTIONS /hello` pre-flight with `Origin` and `Access-Control-Request-Method` headers, and asserts `403 Forbidden` (the 3.5 behaviour) in `preflightWithEmptyConfigShouldBeRejectedOnBoot35()`.

One build note: the test constructs MockMvc manually via `MockMvcBuilders.webAppContextSetup(context)` instead of using `@AutoConfigureMockMvc`. That annotation's package relocates in Boot 4.0, so using it would turn this module into a compile-failure demo and hide the behavioural change we actually want to show.

**Measured on Spring Boot 3.5.16**: the pre-flight returns `403 Forbidden` and the test passes.

**Measured on Spring Boot 4.0.7**: the same pre-flight returns `200 OK` and the test fails. The empty config no longer blocks anything.

Verified 15 July 2026.

## Fix / Migration Path

Explicitly configure your CORS requirements. Do not rely on empty `CorsConfiguration` objects or default-deny behaviour that has now shifted. Use `applyPermitDefaultValues()` if you want simple defaults, or explicitly set allowed origins.

```java
// Spring Boot 4.0 (Recommended Fix)
CorsConfiguration config = new CorsConfiguration();
config.addAllowedOrigin("https://example.com");
config.addAllowedMethod("*");
source.registerCorsConfiguration("/**", config);
```

If the empty config was doing duty as an access-control mechanism, replace it with real security configuration: CORS is a browser courtesy, not a server-side guard.

## References

- [Spring Framework 7.0 Release Notes](https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Release-Notes) — CORS Pre-Flight requests behavior change
- Master list entry: 2.17
