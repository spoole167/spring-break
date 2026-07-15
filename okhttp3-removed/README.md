# OkHttp3ClientHttpRequestFactory removed (Tier 1: Won't Compile)

**Summary**: Spring Framework 7 (Spring Boot 4.0) removes `OkHttp3ClientHttpRequestFactory`, the adapter that let `RestTemplate` and `RestClient` use OkHttp as their HTTP engine. It had been deprecated since Framework 6.1 because OkHttp 3 was end-of-life and the adapter never supported OkHttp's newer versions properly. Any configuration class that wires a `RestTemplate` to OkHttp through this factory stops compiling on Boot 4.0, even though the OkHttp library itself is still happily on the classpath.

## What breaks

In Spring Boot 3.5, backing a `RestTemplate` with OkHttp compiles fine:

```java
import org.springframework.http.client.OkHttp3ClientHttpRequestFactory;

@Configuration
public class OkHttpConfig {

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate(new OkHttp3ClientHttpRequestFactory());
    }
}
```

In Spring Boot 4.0 (Framework 7.0), the factory class is gone from `spring-web`:

```
[ERROR] cannot find symbol
  symbol:   class OkHttp3ClientHttpRequestFactory
```

## How this test works

The pom pulls in `spring-boot-starter-web` plus an explicit `com.squareup.okhttp3:okhttp` 4.12.0 dependency. `OkHttpConfig` declares a `RestTemplate` bean built on `new OkHttp3ClientHttpRequestFactory()`. `OkHttp3RemovedTest` is a `@SpringBootTest` (with a nested `TestApp` as the application class) that autowires the `RestTemplate` and runs two tests: `restTemplateBeanIsNotNull()` checks the bean exists, and `restTemplateUsesOkHttp3Factory()` asserts via `assertInstanceOf` that the request factory really is the OkHttp one.

- On Boot 3.5.16: compiles and passes.
- On Boot 4.0.7: fails at compile with `cannot find symbol: class OkHttp3ClientHttpRequestFactory`. Verified 15 July 2026.

## Fix / Migration Path

Move to one of the request factories Spring still ships:

```java
@Bean
public RestTemplate restTemplate() {
    return new RestTemplate(new JdkClientHttpRequestFactory());
}
```

`JdkClientHttpRequestFactory` (built on `java.net.http.HttpClient`) is the zero-extra-dependency choice; Apache HttpComponents and Jetty-backed factories remain supported if you need their connection-pool tuning. Note the dependency trap: removing the factory does not remove OkHttp. The now-unused `okhttp` jar stays in your build unless you delete it, which is how zombie dependencies are born.
