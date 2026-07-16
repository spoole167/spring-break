# `@WebMvcTest` Relocated to `spring-boot-webmvc-test` (Tier 1: Won't Compile)

**Summary**: Boot 4.0 splits the monolithic `spring-boot-test-autoconfigure` into per-concern test modules. `@WebMvcTest` moved to `spring-boot-webmvc-test` with a parallel package. `@AutoConfigureMockMvc`, `@DataJpaTest`, `@WebFluxTest`, `@DataMongoTest` and most other test slice annotations moved the same way. The annotations keep their semantics; only the import path and the build dependency change.

This module demonstrates the pattern with `@WebMvcTest` because it is the most widely used affected annotation. The migration story is identical for the others.

## What breaks

`spring-boot-test-autoconfigure-4.0.7.jar` is dramatically slimmed: only `AutoConfigureDataSourceInitialization`, `AutoConfigureJson`, `AutoConfigureJsonTesters`, and a few `Json*` slice annotations remain. Every other slice annotation moved to a per-concern test jar:

| Boot 3.5 location | Boot 4.0 jar | Boot 4.0 package |
|---|---|---|
| `org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest` | `spring-boot-webmvc-test` | `org.springframework.boot.webmvc.test.autoconfigure` |
| `org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc` | `spring-boot-webmvc-test` | `org.springframework.boot.webmvc.test.autoconfigure` |
| `org.springframework.boot.test.autoconfigure.web.client.AutoConfigureWebClient` | `spring-boot-webclient-test` | `org.springframework.boot.webclient.test.autoconfigure` |
| `org.springframework.boot.test.autoconfigure.web.client.AutoConfigureMockRestServiceServer` | `spring-boot-restclient-test` | `org.springframework.boot.restclient.test.autoconfigure` |
| `org.springframework.boot.test.autoconfigure.web.reactive.WebFluxTest` | `spring-boot-webflux-test` | `org.springframework.boot.webflux.test.autoconfigure` |
| `org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest` | `spring-boot-data-jpa-test` | `org.springframework.boot.data.jpa.test.autoconfigure` |
| `org.springframework.boot.test.autoconfigure.data.mongo.DataMongoTest` | `spring-boot-data-mongodb-test` | `org.springframework.boot.data.mongodb.test.autoconfigure` |
| `org.springframework.boot.test.autoconfigure.jdbc.JdbcTest` | `spring-boot-jdbc-test` | `org.springframework.boot.jdbc.test.autoconfigure` |
| `org.springframework.boot.test.autoconfigure.web.client.RestClientTest` | `spring-boot-restclient-test` | `org.springframework.boot.restclient.test.autoconfigure` |
| `org.springframework.boot.test.autoconfigure.graphql.GraphQlTest` | `spring-boot-graphql-test` | `org.springframework.boot.graphql.test.autoconfigure` |

The `Data*Test` family (`DataRedisTest`, `DataLdapTest`, `DataR2dbcTest`, `DataNeo4jTest`, `DataElasticsearchTest`, `DataCassandraTest`, `DataCouchbaseTest`, `DataJdbcTest`, etc.) follows the same pattern with `spring-boot-data-{tech}-test` artifacts.

`@AutoConfigureObservability` is the exception: Boot 4 **removed it entirely** rather than relocating it. See the sibling test module `auto-configure-observability-removed`.

## How this test works

`HelloControllerTest` imports `@WebMvcTest` from the Boot-3 package and uses MockMvc to test a simple controller. The test class declares only `spring-boot-starter-test`, with no per-concern test module.

Run `mvn test` on Boot 3.5.16 and `@WebMvcTest` resolves via `spring-boot-test-autoconfigure-3.5.16`, MockMvc is wired, and the controller test passes. Run `mvn test-compile -Dspring-boot.version=4.0.7` and compilation fails:

```
HelloControllerTest.java:[5,63] package org.springframework.boot.test.autoconfigure.web.servlet does not exist
HelloControllerTest.java:[53,2] cannot find symbol
```

On Boot 3.5.16: test passes. On Boot 4.0.7: compile fails on the missing `web.servlet` package. Verified 15 July 2026.

## Fix / Migration Path

Two steps, both mechanical:

1. Add the per-concern test dependency:
   ```xml
   <dependency>
     <groupId>org.springframework.boot</groupId>
     <artifactId>spring-boot-webmvc-test</artifactId>
     <scope>test</scope>
   </dependency>
   ```

   Or use the per-concern test starter (`spring-boot-starter-webmvc-test`), which bundles related dependencies.

2. Update the import:
   ```diff
   - import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
   + import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
   ```

The annotation usage and semantics are unchanged. Tests that previously worked will work again after the import and dependency update.

## References

- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- Sibling module: `auto-configure-observability-removed` (removed entirely, no replacement)
