# `@JsonComponent` Renamed to `@JacksonComponent` (Tier 1: Won't Compile)

**Summary**: Spring Boot 4.0 renames Spring Boot's `@JsonComponent` and `@JsonMixin` annotations to `@JacksonComponent` and `@JacksonMixin` to align with Jackson 3 branding. The annotations also changed jar, moving from `spring-boot` core to `spring-boot-jackson`, the new per-concern module. The package stays the same: `org.springframework.boot.jackson.*`. Code that imports the old names fails to compile.

## What breaks

| | Boot 3.5.16 | Boot 4.0.7 |
|---|---|---|
| `@JsonComponent` | `org.springframework.boot.jackson.JsonComponent` in `spring-boot-3.5.16.jar` | absent |
| `@JsonMixin` | `org.springframework.boot.jackson.JsonMixin` in `spring-boot-3.5.16.jar` | absent |
| `@JacksonComponent` | absent | `org.springframework.boot.jackson.JacksonComponent` in `spring-boot-jackson-4.0.7.jar` |
| `@JacksonMixin` | absent | `org.springframework.boot.jackson.JacksonMixin` in `spring-boot-jackson-4.0.7.jar` |

Empirically verified by jar inspection.

## How this test works

`CustomSerializerMarker` is annotated with `@JsonComponent` (the Boot 3 import) and **deliberately does not extend a Jackson serializer class**. The cheat-sheet card's original `no_module_reason` claimed the rename couldn't be tested in isolation because Jackson 3 also moved `JsonSerializer` to a different package. That is only true for a class that both uses `@JsonComponent` and extends `JsonSerializer`. Decoupling the two isolates the annotation-rename failure cleanly: the annotation alone is the load-bearing piece, and the test proves only that.

Run `mvn test` on Boot 3.5.16 and the annotation resolves at `org.springframework.boot.jackson.JsonComponent`; the test passes. Run `mvn compile -Dspring-boot.version=4.0.7` and compilation fails:

```
CustomSerializerMarker.java:[3,40] package org.springframework.boot.jackson does not exist
CustomSerializerMarker.java:[33,2] cannot find symbol
```

On Boot 3.5.16: compiles, runs, passes. On Boot 4.0.7: compile fails on the missing `org.springframework.boot.jackson` package. Verified 15 July 2026.

## Fix / Migration Path

1. Rename the import: `JsonComponent` → `JacksonComponent`, `JsonMixin` → `JacksonMixin`. The package (`org.springframework.boot.jackson`) is unchanged.
2. Rename the annotation usages.
3. Add `spring-boot-jackson` (or use `spring-boot-starter-jackson`) if your build doesn't pull it in transitively. Most web apps already get it via `spring-boot-starter-web`.

```diff
- import org.springframework.boot.jackson.JsonComponent;
+ import org.springframework.boot.jackson.JacksonComponent;

- @JsonComponent
+ @JacksonComponent
  public class MoneySerializer extends JsonSerializer<Money> { ... }
```

## Watch out

If your custom serializer also extends `JsonSerializer` from Jackson 2's package (`com.fasterxml.jackson.databind.JsonSerializer`), you hit a second compile error: Jackson 3 moved that class to `tools.jackson.databind.JsonSerializer`. Both renames need to land together. The Jackson 3 group-ID migration is covered separately by the `jackson-group-id` module and card.

## References

- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- Sibling modules: `jackson-group-id`, `jackson-class-renames`
