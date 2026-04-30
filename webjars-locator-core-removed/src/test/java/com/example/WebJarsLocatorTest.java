package com.example;

import org.junit.jupiter.api.Test;
import org.webjars.WebJarAssetLocator;
import static org.junit.jupiter.api.Assertions.assertNotNull;

class WebJarsLocatorTest {

    @Test
    void webjarsLocatorCoreIsAvailableOnBoot35() {
        // Direct instantiation — fails to compile on Boot 4.0 where
        // webjars-locator-core is removed from managed dependencies.
        WebJarAssetLocator locator = new WebJarAssetLocator();
        assertNotNull(locator);
    }
}
