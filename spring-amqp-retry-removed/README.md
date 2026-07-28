# `RabbitRetryTemplateCustomizer` Removed (Tier 1: Won't Compile)

**Summary**: Spring AMQP 4.0 (Spring Boot 4.0) drops its Spring Retry dependency
and removes `org.springframework.boot.autoconfigure.amqp.RabbitRetryTemplateCustomizer`.
Every bean implementing it fails to compile. Publisher and consumer retry are
now configured through separate customiser interfaces.

## How this test works

`RetryCustomizerUsage` builds a `RabbitRetryTemplateCustomizer` the way a
typical Boot 3.5 app does.

- Boot 3.5.16: compiles, test passes.
- Boot 4.0.x: `cannot find symbol: class RabbitRetryTemplateCustomizer` at compile.

Verified 2026-07-27 on 3.5.16 (pass) and 4.0.7 (compile failure).
