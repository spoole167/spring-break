# Jackson 3 package move breaks custom serialisers (Tier 1: Won't Compile)

**Summary**: Spring Boot 4.0 moves from Jackson 2 to Jackson 3, which relocated the whole library from `com.fasterxml.jackson` to `tools.jackson` and renamed the core extension classes along the way. Every custom serialiser or deserialiser written against Jackson 2's `JsonSerializer` / `JsonDeserializer` API fails to compile on Boot 4.0, because the packages it imports no longer exist on the classpath.

## What breaks

In Spring Boot 3.5 (Jackson 2.x), a custom serialiser looks like this and compiles fine:

```java
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.SerializerProvider;

public class MoneySerializer extends JsonSerializer<Long> {

    @Override
    public void serialize(Long cents, JsonGenerator gen, SerializerProvider serializers)
            throws IOException {
        gen.writeString(String.format("%.2f", cents / 100.0));
    }
}
```

In Spring Boot 4.0 (Jackson 3), the imports fail before anything else gets a chance to:

```
[ERROR] package com.fasterxml.jackson.core does not exist
```

## How this test works

`MoneySerializer` extends `JsonSerializer<Long>` and formats a cents value as a currency string (1099 becomes "10.99"). `MoneyDeserializer` extends `JsonDeserializer<Long>` and parses it back. `Product` is a DTO whose `priceCents` field wires both in via `@JsonSerialize(using = ...)` and `@JsonDeserialize(using = ...)`. `JacksonClassRenamesTest` is a `@SpringBootTest` that autowires the `ObjectMapper` and runs two tests: `customSerializerShouldFormatPriceAsCurrency()` asserts the JSON contains "10.99", and `customDeserializerShouldParseCurrencyToCents()` asserts the round trip yields 1099.

- On Boot 3.5.16: compiles and passes.
- On Boot 4.0.7: fails at compile with `package com.fasterxml.jackson.core does not exist` (Jackson 3 moved to `tools.jackson`). Verified 15 July 2026.

## Fix / Migration Path

This is not a find-and-replace on the package prefix. Jackson 3 renamed the extension points as well as relocating them:

- `JsonSerializer` becomes `ValueSerializer` (under `tools.jackson.databind`)
- `JsonDeserializer` becomes `ValueDeserializer`
- `SerializerProvider` becomes `SerializationContext`
- `JsonParser` and `JsonGenerator` keep their names but move to the `tools.jackson.core` package, and checked `IOException` signatures change

Each custom serialiser needs its superclass, method signatures and imports reworked against the Jackson 3 API. The `@JsonSerialize` / `@JsonDeserialize` annotations survive with their Jackson 3 equivalents, so the wiring pattern stays the same even though the implementations must be rewritten.
