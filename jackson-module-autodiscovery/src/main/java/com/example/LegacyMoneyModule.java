package com.example;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.databind.ser.std.StdSerializer;

import java.io.IOException;

/**
 * Jackson 2 module registered ONLY via
 * META-INF/services/com.fasterxml.jackson.databind.Module.
 * Boot 3.5 does not ServiceLoader-scan for modules, so this stays inactive
 * unless someone calls findAndRegisterModules() themselves.
 */
public class LegacyMoneyModule extends SimpleModule {

    public LegacyMoneyModule() {
        super("legacy-money-module");
        addSerializer(Money.class, new StdSerializer<>(Money.class) {
            @Override
            public void serialize(Money value, JsonGenerator gen, SerializerProvider provider)
                    throws IOException {
                gen.writeString(value.getAmount().toPlainString() + " " + value.getCurrency());
            }
        });
    }
}
