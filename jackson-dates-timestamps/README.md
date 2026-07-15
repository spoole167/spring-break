# write-dates-as-timestamps Property Breaks Startup (Tier 2: Won't Run)

**Summary**: `spring.jackson.serialization.write-dates-as-timestamps=true` works on Spring Boot 3.5 and stops the application from starting on Spring Boot 4.0. Jackson 3 moved the date/time toggles out of `SerializationFeature`, and Boot 4.0 binds `spring.jackson.serialization.*` keys against the new enum, so the old value fails enum conversion and property binding aborts context startup.

## What breaks

A single leftover line in `application.properties` (or, as here, test properties):

```properties
spring.jackson.serialization.write-dates-as-timestamps=true
```

On Boot 3.5 the property is honoured: the auto-configured `ObjectMapper` writes `Instant` fields as numeric millisecond timestamps. On Boot 4.0.7 the context never starts:

```
org.springframework.boot.context.properties.bind.BindException:
  Failed to bind properties under 'spring.jackson.serialization' to
  java.util.Map<tools.jackson.databind.SerializationFeature, Boolean>
Caused by: java.lang.IllegalArgumentException: No enum constant
  tools.jackson.databind.SerializationFeature.write-dates-as-timestamps
```

The code compiles on both versions. Nothing is deprecated, nothing warns. The failure arrives at startup.

## How this test works

`JacksonDatesTimestampsTest` sets the property via `@SpringBootTest(properties = ...)`, resolves the auto-configured `ObjectMapper` reflectively (so the same test code works against Jackson 2's `com.fasterxml.jackson` and Jackson 3's `tools.jackson`), serialises a map containing an `Instant`, and asserts the value is numeric.

- On Boot 3.5.16: context starts, the property is honoured, both tests pass.
- On Boot 4.0.7: the context fails to load with the `BindException` above; the assertions are never reached. Verified 15 July 2026.

## Fix / Migration Path

Remove the property. If you must keep numeric timestamps, enable the feature programmatically against Jackson 3's API (the date/time toggles now live in their own feature set), or set the format per field:

```java
@JsonFormat(shape = JsonFormat.Shape.NUMBER)
private Instant timestamp;
```

Then audit every other `spring.jackson.serialization.*` and `spring.jackson.deserialization.*` entry: any value naming an enum constant that Jackson 3 moved or removed fails startup the same way.
