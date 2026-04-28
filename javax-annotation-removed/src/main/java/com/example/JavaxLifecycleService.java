package com.example;

import javax.annotation.PostConstruct;
import javax.inject.Inject;
import org.springframework.stereotype.Component;
import org.springframework.context.ApplicationContext;

@Component
public class JavaxLifecycleService {

    @Inject
    private ApplicationContext context;

    private boolean postConstructCalled = false;

    @PostConstruct
    public void init() {
        this.postConstructCalled = true;
    }

    public boolean isPostConstructCalled() {
        return postConstructCalled;
    }

    public ApplicationContext getContext() {
        return context;
    }
}
