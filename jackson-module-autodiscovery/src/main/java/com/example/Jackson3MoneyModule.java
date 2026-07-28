package com.example;

import tools.jackson.core.JsonGenerator;
import tools.jackson.databind.SerializationContext;
import tools.jackson.databind.module.SimpleModule;
import tools.jackson.databind.ser.std.StdSerializer;

/**
 * Jackson 3 flavour of the same module, registered ONLY via
 * META-INF/services/tools.jackson.databind.JacksonModule.
 * Jackson 3 (Boot 4.0) finds and registers classpath modules automatically:
 * this serializer silently activates and changes the JSON schema.
 */
public class Jackson3MoneyModule extends SimpleModule {

    public Jackson3MoneyModule() {
        super("jackson3-money-module");
        addSerializer(Money.class, new StdSerializer<>(Money.class) {
            @Override
            public void serialize(Money value, JsonGenerator gen, SerializationContext ctxt) {
                gen.writeString(value.getAmount().toPlainString() + " " + value.getCurrency());
            }
        });
    }
}
