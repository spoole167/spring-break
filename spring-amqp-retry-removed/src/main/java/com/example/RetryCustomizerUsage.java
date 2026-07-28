package com.example;

import org.springframework.boot.autoconfigure.amqp.RabbitRetryTemplateCustomizer;
import org.springframework.retry.support.RetryTemplate;

/**
 * Uses RabbitRetryTemplateCustomizer the way a typical Boot 3.5 application
 * does: one customizer bean tuning both publisher and consumer retry.
 *
 * Boot 3.5: compiles (deprecated at most).
 * Boot 4.0: "cannot find symbol: class RabbitRetryTemplateCustomizer" —
 * Spring AMQP 4 dropped Spring Retry; publisher and consumer retry now have
 * separate customiser interfaces.
 */
public class RetryCustomizerUsage {

    public RabbitRetryTemplateCustomizer retryCustomizer() {
        return new RabbitRetryTemplateCustomizer() {
            @Override
            public void customize(Target target, RetryTemplate retryTemplate) {
                // tune retryTemplate the same way for SENDER and LISTENER
            }
        };
    }
}
