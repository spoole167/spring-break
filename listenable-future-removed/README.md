# ListenableFuture removed (Tier 1: Won't Compile)

**Summary**: Spring's own async future type, `org.springframework.util.concurrent.ListenableFuture`, along with `SettableListenableFuture` and the callback interfaces, is removed in Spring Framework 7 (Spring Boot 4.0) in favour of the JDK's `CompletableFuture` (spring-framework#33809). It had been deprecated since Framework 6, but any service signature, callback chain or test that still mentions the type stops compiling on Boot 4.0.

## What breaks

In Spring Boot 3.5, returning a `ListenableFuture` compiles (with deprecation warnings):

```java
import org.springframework.util.concurrent.ListenableFuture;
import org.springframework.util.concurrent.SettableListenableFuture;

@Service
public class AsyncService {

    public ListenableFuture<String> fetchData() {
        SettableListenableFuture<String> future = new SettableListenableFuture<>();
        future.set("data-from-service");
        return future;
    }
}
```

In Spring Boot 4.0 (Framework 7.0), the classes are gone:

```
[ERROR] cannot find symbol
  symbol:   class ListenableFuture
```

## How this test works

`AsyncService.fetchData()` builds a `SettableListenableFuture<String>`, completes it with the value `"data-from-service"`, and returns it as a `ListenableFuture<String>`. `ListenableFutureTest.fetchDataReturnsExpectedValue()` calls the service, blocks on `future.get()`, and asserts the value. The test itself imports `ListenableFuture` too, so both the main and test source trees break on 4.0.

- On Boot 3.5.16: compiles and passes.
- On Boot 4.0.7: fails at compile with `cannot find symbol: class ListenableFuture` (removed in Spring Framework 7 in favour of CompletableFuture, spring-framework#33809). Verified 15 July 2026.

## Fix / Migration Path

Replace `ListenableFuture` with `java.util.concurrent.CompletableFuture` throughout:

```java
public CompletableFuture<String> fetchData() {
    return CompletableFuture.completedFuture("data-from-service");
}
```

Callback-style code (`addCallback(success, failure)`) maps to `whenComplete` or `thenAccept`/`exceptionally`. `CompletableFuture` has been the recommended type since the deprecation in Framework 6, so this migration can be done entirely on Boot 3.5 before the upgrade. The awkward cases are public API signatures and third-party libraries that still expose `ListenableFuture`: those need coordinating, not just editing.
