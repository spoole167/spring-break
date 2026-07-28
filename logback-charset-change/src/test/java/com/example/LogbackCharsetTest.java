package com.example;

import org.junit.jupiter.api.Test;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.context.ConfigurableApplicationContext;

import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Surefire runs this JVM with -Dfile.encoding=ISO-8859-1 so the platform
 * default charset is NOT UTF-8.
 *
 * Boot 3.5: the default Logback file appender writes in the platform default
 * charset. "Müller" is logged as 0x4D 0xFC ... (ü = 0xFC) -> test passes.
 *
 * Boot 4.0: the file appender charset is forced to UTF-8 regardless of the
 * platform default. ü becomes 0xC3 0xBC -> test fails. Any downstream tool
 * still reading the file with the platform charset sees "MÃ¼ller".
 */
class LogbackCharsetTest {

    @Test
    void fileAppenderUsesPlatformDefaultCharset() throws Exception {
        // Unique name per run: avoids needing to delete stale files, which
        // some build environments (mounted filesystems) refuse.
        Path logFile = Path.of("target", "charset-test-" + System.nanoTime() + ".log");

        ConfigurableApplicationContext ctx = SpringApplication.run(LogApp.class,
                "--spring.main.web-application-type=none",
                "--logging.file.name=" + logFile);
        LoggerFactory.getLogger(LogbackCharsetTest.class).info("Order confirmed for Müller");
        ctx.close();

        byte[] bytes = Files.readAllBytes(logFile);
        String platformDecoded = new String(bytes, Charset.defaultCharset());

        assertTrue(Charset.defaultCharset().name().equals("ISO-8859-1"),
                "Test setup: surefire should have set -Dfile.encoding=ISO-8859-1, got "
                + Charset.defaultCharset());
        assertTrue(platformDecoded.contains("Order confirmed for Müller"),
                "Log file is no longer written in the platform default charset ("
                + Charset.defaultCharset() + "). Boot forced UTF-8: tools reading "
                + "the file with the platform charset now see mojibake.");
    }
}
