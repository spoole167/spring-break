# webjars-locator-core support removed (Tier 1: Won't Compile)

**Summary**: Spring Framework 7.0 drops WebJars support built on `org.webjars:webjars-locator-core` in favour of `org.webjars:webjars-locator-lite`, and Spring Boot 4.0 drops dependency management for the old artifact. Code using `WebJarAssetLocator` from the core locator no longer compiles on 4.0.

## What breaks

In Spring Boot 3.5, `webjars-locator-core` is version-managed by the BOM and `WebJarAssetLocator` resolves WebJar asset paths:

```java
WebJarAssetLocator locator = new WebJarAssetLocator();
String path = locator.getFullPath("jquery", "jquery.min.js");
```

On Spring Boot 4.0 the artifact falls out of dependency management and the Framework-side integration is gone:

```
[ERROR] cannot find symbol
  symbol:   class WebJarAssetLocator
```

## How this test works

`WebJarsUsage` calls `WebJarAssetLocator` directly. On Boot 3.5.16 the module compiles and its test passes; on Boot 4.0.7 it fails at compile. Verified 15 July 2026.

## Fix / Migration Path

Move to `org.webjars:webjars-locator-lite` (the replacement Spring uses), and its `WebJarVersionLocator` API. If you only serve WebJar assets via Spring MVC resource handling with version-agnostic paths, the lite locator is picked up automatically.

## Source

Spring Framework 7.0 Release Notes ("Removed APIs" section):

> Many other APIs and features were removed as part of [#33809](https://github.com/spring-projects/spring-framework/issues/33809), including: [...] WebJars support with `org.webjars:webjars-locator-core` in favor of `org.webjars:webjars-locator-lite`

https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Release-Notes
