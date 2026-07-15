# OpenSaml4AuthenticationProvider removed (Tier 1: Won't Compile)

**Summary**: Spring Security 7 (Spring Boot 4.0) drops support for OpenSAML 4 and requires OpenSAML 5. The class most SAML setups touch directly, `OpenSaml4AuthenticationProvider`, is deleted along with the rest of the OpenSAML 4 integration; the replacements are the `OpenSaml5*` classes. Any security configuration that references the OpenSAML 4 provider stops compiling on Boot 4.0.

## What breaks

In Spring Boot 3.5 (Spring Security 6), referencing the provider compiles fine:

```java
import org.springframework.security.saml2.provider.service.authentication.OpenSaml4AuthenticationProvider;

OpenSaml4AuthenticationProvider provider = new OpenSaml4AuthenticationProvider();
```

In Spring Boot 4.0 (Spring Security 7), the class is gone:

```
[ERROR] cannot find symbol
  symbol:   class OpenSaml4AuthenticationProvider
```

## How this test works

The pom pulls in `spring-boot-starter-security` and `spring-security-saml2-service-provider`, with the transitive OpenSAML and Shibboleth artifacts excluded: the module only needs the Spring Security class on the compile classpath, not a running SAML stack (which would also drag in the Shibboleth repository). `SamlConfig.getSamlProviderClassName()` returns the provider's fully qualified name as a string, which compiles on both versions. The actual tripwire is `OpenSaml4RemovedTest.openSaml4AuthenticationProviderShouldExistOnClasspath()`, which references `OpenSaml4AuthenticationProvider.class` directly and asserts its name is non-null.

- On Boot 3.5.16: compiles and passes.
- On Boot 4.0.7: fails at compile with `cannot find symbol: class OpenSaml4AuthenticationProvider` (Spring Security 7 requires OpenSAML 5). Verified 15 July 2026.

## Fix / Migration Path

Move to the OpenSAML 5 equivalents: Spring Security ships `OpenSaml5AuthenticationProvider` and matching `OpenSaml5*` classes for the other integration points (logout, metadata, authentication requests). This is more than a class rename, because the underlying OpenSAML library jumps a major version too: your `opensaml-*` dependencies must move to the 5.x line, and OpenSAML 5 requires a newer Java baseline. The `OpenSaml5*` classes are already available in Spring Security 6.4+ on Boot 3.5, so you can switch over and test on 3.5 before attempting the Boot 4 upgrade.
