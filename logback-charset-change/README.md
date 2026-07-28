# Logback File Appender Forced to UTF-8 (Tier 3: Different Results)

**Summary**: Boot 3.5's default Logback file appender writes in the platform
default charset. Boot 4.0 forces UTF-8. Downstream tools still reading the log
with the platform charset see mojibake ("MÃ¼ller"). No error, just wrong bytes.

## How this test works

Surefire runs the test JVM with `-Dfile.encoding=ISO-8859-1` so the platform
default is visibly non-UTF-8 on any build machine. The test boots the app with
`logging.file.name`, logs "Müller", and decodes the file with the platform
charset.

- Boot 3.5.16: file is ISO-8859-1 (ü = 0xFC), round-trips, test passes.
- Boot 4.0.x: file is UTF-8 (ü = 0xC3 0xBC), platform decode garbles it, test fails.

Verified 2026-07-27 on 3.5.16 (pass) and 4.0.7 (fail: file written as UTF-8).
