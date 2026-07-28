package com.example.app;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Lives in com.example.app so component scanning does NOT reach
 * com.example.legacylib. The auto-configurations there can only enter the
 * context via their registration files (spring.factories vs
 * AutoConfiguration.imports) — which is exactly what this module tests.
 */
@SpringBootApplication
public class FactoriesApp {
    public static void main(String[] args) {
        SpringApplication.run(FactoriesApp.class, args);
    }
}
