package com.example.legacylib;

import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.context.annotation.Bean;

/** Registered ONLY via META-INF/spring.factories (the pre-Boot-2.7 mechanism). */
@AutoConfiguration
public class LegacyAutoConfiguration {

    public static class LegacyMarker {
    }

    @Bean
    public LegacyMarker legacyMarker() {
        return new LegacyMarker();
    }
}
