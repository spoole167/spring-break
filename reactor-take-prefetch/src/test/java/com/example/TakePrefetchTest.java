package com.example;

import org.junit.jupiter.api.Test;
import reactor.core.publisher.Flux;

import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Category (d) — Runs on Both, Different Behaviour
 *
 * Demonstrates the Reactor take(n) prefetch behaviour change.
 *
 * Spring Boot 3.5 (Reactor 2024.0):
 *   Flux.take(n) requests unbounded (Long.MAX_VALUE) from upstream, then stops
 *   after receiving n items. Upstream sources produce more than needed.
 *
 * Spring Boot 4.0 (Reactor 2025.0):
 *   Flux.take(n) now requests exactly n items from upstream. Aligns backpressure
 *   semantics with actual subscriber demand.
 *
 * This is a "different behaviour" breaking change: both versions emit n items,
 * but backpressure, resource consumption, and metrics differ silently.
 *
 * References:
 * - Reactor Core Release Notes: https://github.com/reactor/reactor-core/releases
 * - Reactor 2025.0 Release: https://github.com/reactor/reactor-core/releases/tag/v3.7.0
 * - Reactive Streams (backpressure): http://www.reactive-streams.org/
 * - Spring Boot 4.0 Migration Guide: https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
 */
class TakePrefetchTest {

    @Test
    void takeShouldRequestUnboundedOnReactor2024() {
        AtomicLong requestedCount = new AtomicLong(0);

        Flux<Integer> source = Flux.range(1, 100)
            .doOnRequest(n -> requestedCount.addAndGet(n));

        // Block and collect — no StepVerifier dependency needed
        List<Integer> items = source.take(5).collectList().block();

        assertNotNull(items);
        assertEquals(5, items.size(), "Should emit exactly 5 items");

        // Reactor 2024.0 (Boot 3.5): take(5) requests Long.MAX_VALUE (unbounded)
        // Reactor 2025.0 (Boot 4.0): take(5) requests exactly 5
        assertEquals(
            Long.MAX_VALUE, requestedCount.get(),
            "Expected unbounded request (Long.MAX_VALUE) from take(5), but got " +
            requestedCount.get() + ". Reactor 2025.0 changed take(n) to request exactly n."
        );
    }

    @Test
    void takeShouldYieldExactlyFiveItems() {
        // Both versions emit exactly 5 items — this test passes on both
        AtomicLong itemCount = new AtomicLong(0);

        List<Integer> items = Flux.range(1, 100)
            .doOnNext(n -> itemCount.incrementAndGet())
            .take(5)
            .collectList()
            .block();

        assertNotNull(items);
        assertEquals(List.of(1, 2, 3, 4, 5), items, "Should emit items 1-5");
        assertEquals(5, itemCount.get(), "Should emit exactly 5 items");
    }

    @Test
    void takeShouldCancelUpstreamAfterN() {
        // Verify that take(n) cancels the upstream after n items
        AtomicLong onCancelCount = new AtomicLong(0);

        List<Integer> items = Flux.range(1, 1000)
            .doOnCancel(() -> onCancelCount.incrementAndGet())
            .take(10)
            .collectList()
            .block();

        assertNotNull(items);
        assertEquals(10, items.size(), "Should emit 10 items");

        // On both versions: upstream should be cancelled after take(10) completes
        assertEquals(1, onCancelCount.get(), "Upstream should be cancelled once");
    }
}
