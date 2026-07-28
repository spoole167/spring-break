package com.example.legacylib;

import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.context.annotation.Bean;

/** Registered ONLY via META-INF/spring/AutoConfiguration.imports (the current mechanism). */
@AutoConfiguration
public class ModernAutoConfiguration {

    public static class ModernMarker {
    }

    @Bean
    public ModernMarker modernMarker() {
        return new ModernMarker();
    }
}
