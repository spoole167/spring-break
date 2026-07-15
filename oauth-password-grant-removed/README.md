# OAuth 2.0 Password Grant Removed (Tier 1: Won't Compile)

AuthorizationGrantType.PASSWORD removed per OAuth 2.1 security best practices; migrate to Authorization Code or Client Credentials.

## What Breaks

Spring Security 7 (Spring Boot 4.0) removes the `AuthorizationGrantType.PASSWORD` constant. Any Java code that references it stops compiling.

**Code that breaks:**
```java
.authorizationGrantType(AuthorizationGrantType.PASSWORD)
```

**Measured on Spring Boot 4.0.7 (clean build):**
```
[ERROR] cannot find symbol: variable PASSWORD
```

This module builds a `ClientRegistration` with the constant in Java, so the removal shows up at compile time.

**The runtime variant.** Applications that never mention the constant in code, but request the password grant through configuration or in token requests, compile cleanly and instead hit runtime "unsupported grant type" errors:
```properties
spring.security.oauth2.client.registration.example.authorization-grant-type=password
```
Same removal, different failure point. This module demonstrates the compile-time variant.

## Why It Was Removed

OAuth 2.1 and RFC 9700 explicitly deprecate the password grant because it violates core OAuth security principles:

1. **User credentials exposed**: Requires users to share passwords directly with the application (not an OAuth client)
2. **No refresh tokens**: Often implemented without refresh token rotation
3. **Poor for public clients**: Not suitable for mobile/SPA applications
4. **Security anti-pattern**: Direct password handling contradicts OAuth 2.0/2.1 design

## How This Test Works

The module wires up a password-grant client the way a 3.5-era application would:

- **OAuth2Config.java**: Builds a `ClientRegistration` for registration id "example" using `AuthorizationGrantType.PASSWORD` and registers it in an `InMemoryClientRegistrationRepository`. This is the line that stops compiling on 4.0.
- **OAuth2PasswordGrantTest.testPasswordGrantConfigurationExists()**: Checks the ClientRegistrationRepository loads.
- **OAuth2PasswordGrantTest.testClientRegistrationForPasswordGrant()**: Retrieves the "example" registration and verifies the client setup.
- **OAuth2PasswordGrantTest.testPasswordGrantUnsupported()**: References `AuthorizationGrantType.PASSWORD` directly, documenting the removal at the exact symbol that disappears.

application.properties also configures `authorization-grant-type=password`, showing the configuration-based form of the same problem.

Verified 15 July 2026.

## On Spring Boot 3.5.16

```bash
mvn clean test
```

Output: Tests pass. The PASSWORD grant type exists and is accessible.

## On Spring Boot 4.0.7

Compilation fails:
```
[ERROR] cannot find symbol: variable PASSWORD
```

No tests run. An application that only used the grant via configuration or token requests would compile, then fail at runtime with "unsupported grant type" errors.

## Fix / Migration Path

Identify your use case and migrate to an appropriate OAuth 2.0 / 2.1 grant type:

**1. Audit configuration:**
```bash
grep -r "authorization-grant-type.*password" src/main/resources/
grep -r "AuthorizationGrantType.PASSWORD" src/
```

**2. Migrate based on use case:**

**User Interactive Login (Web/SPA/Mobile) — Use Authorization Code with PKCE:**
```properties
spring.security.oauth2.client.registration.myapp.client-id=your-client-id
spring.security.oauth2.client.registration.myapp.client-secret=your-secret
spring.security.oauth2.client.registration.myapp.authorization-grant-type=authorization_code
spring.security.oauth2.client.provider.myapp.authorization-uri=https://auth-server.com/oauth/authorize
spring.security.oauth2.client.provider.myapp.token-uri=https://auth-server.com/oauth/token
spring.security.oauth2.client.provider.myapp.user-info-uri=https://auth-server.com/oauth/userinfo
```

**Server-to-Server (Backend) — Use Client Credentials:**
```properties
spring.security.oauth2.client.registration.backend.client-id=your-client-id
spring.security.oauth2.client.registration.backend.client-secret=your-secret
spring.security.oauth2.client.registration.backend.authorization-grant-type=client_credentials
spring.security.oauth2.client.provider.backend.token-uri=https://auth-server.com/oauth/token
```

**Code migration example:**

Before (Spring Boot 3.5):
```java
ClientRegistration registration = ClientRegistration
    .withRegistrationId("api")
    .clientId("client-id")
    .authorizationGrantType(AuthorizationGrantType.PASSWORD)
    .tokenUri("https://api.example.com/token")
    .build();
```

After (Spring Boot 4.0):
```java
ClientRegistration registration = ClientRegistration
    .withRegistrationId("api")
    .clientId("client-id")
    .authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
    .authorizationUri("https://api.example.com/authorize")
    .tokenUri("https://api.example.com/token")
    .redirectUri("http://localhost:8080/login/oauth2/code/api")
    .userInfoUri("https://api.example.com/userinfo")
    .build();
```

## References

- Spring Security 7.0 Migration: https://docs.spring.io/spring-security/reference/6.5/migration-7/configuration.html
- OAuth 2.1 Security Best Current Practice: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics
- OAuth 2.0 Password Grant Removal: https://datatracker.ietf.org/doc/html/rfc9700
- Spring Boot 4.0 Migration Guide: https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
