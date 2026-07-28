# Jackson 3 Auto-Discovers Classpath Modules (Tier 3: Different Results)

**Summary**: Boot 4.0 / Jackson 3 finds and registers every ServiceLoader-visible
Jackson module on the classpath. Boot 3.5 / Jackson 2 does not. A module that
arrives as a transitive dependency silently changes your JSON output.

## How this test works

A `Money` serializer module ships in this jar registered ONLY through
ServiceLoader files (both the Jackson 2 SPI `com.fasterxml.jackson.databind.Module`
and the Jackson 3 SPI `tools.jackson.databind.JacksonModule`). Nothing registers
it explicitly. The test serialises `Money(150.00, "EUR")` with the
auto-configured mapper (reflection, because the mapper type differs between
Jackson generations):

- Boot 3.5.16: module ignored → `{"amount":150.00,"currency":"EUR"}` → pass.
- Boot 4.0.x: module auto-registered → `"150.00 EUR"` → fail.
  No error, no warning: the JSON schema changed because a jar was present.

Fix on 4.0: `spring.jackson.find-and-add-modules=false`, or audit the classpath.

Both Jackson generations are pinned as explicit dependencies so both module
flavours compile on both Boot versions (the 4.0 BOM no longer manages
`com.fasterxml` artifacts; the 3.5 BOM doesn't manage `tools.jackson`).

Verified 2026-07-27 on 3.5.16 (pass) and 4.0.7 (fail with "150.00 EUR").
