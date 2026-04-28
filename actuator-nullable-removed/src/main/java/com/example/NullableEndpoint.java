package com.example;

import org.springframework.boot.actuate.endpoint.annotation.Endpoint;
import org.springframework.boot.actuate.endpoint.annotation.ReadOperation;
import org.springframework.lang.Nullable;
import org.springframework.stereotype.Component;

@Component
@Endpoint(id = "nullable")
public class NullableEndpoint {

    @ReadOperation
    public String get(@Nullable String name) {
        // In Spring Boot 4.0, org.springframework.lang.Nullable is deprecated/removed
        // on endpoint parameters in favor of JSpecify @Nullable.
        // Actually the documentation says support for it was removed.
        return "Hello " + (name != null ? name : "World");
    }
}
