package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class JavaxAnnotationTest {

    @Autowired
    private JavaxLifecycleService service;

    @Test
    void javaxAnnotationsShouldBeProcessed() {
        assertNotNull(service.getContext(), "@javax.inject.Inject failed: Field was not injected by Spring.");
        assertTrue(service.isPostConstructCalled(), "@javax.annotation.PostConstruct failed: Method was not called by Spring.");
    }
}
