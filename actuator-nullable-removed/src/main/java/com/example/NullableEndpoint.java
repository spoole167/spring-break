package com.example;

import org.springframework.boot.actuate.endpoint.annotation.Endpoint;
import org.springframework.boot.actuate.endpoint.annotation.ReadOperation;
import org.jspecify.annotations.Nullable;
import org.springframework.stereotype.Component;

@Component
@Endpoint(id = "nullable")
public class NullableEndpoint {

    @ReadOperation
    public String get(@Nullable String name) {
        return "Hello " + (name != null ? name : "World");
    }
}