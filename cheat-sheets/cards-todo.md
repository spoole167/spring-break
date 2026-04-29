# Cheat-Sheet Cards — Coverage TODO

**Goal:** Every Tier 1 (Category A) module in the spring-break suite must have a corresponding card in `cheat-sheets/cards/`.

**Date:** 2026-04-29
**Completed:** 2026-04-29
**Status:** ✅ All done — 38 Tier 1 modules fully covered

---

## Fix required (1)

- [x] **javax-inject-removed.yaml** — footer link URL corrected to `javax-annotation-removed`.

---

## Cards created (20)

| # | Module | Notes |
|---|---|---|
| 1 | `bootstrap-registry-relocated` | BootstrapRegistry / EnvironmentPostProcessor package move |
| 2 | `testrest-template-removed` | TestRestTemplate removed from test.web.client |
| 3 | `httpheaders-multivaluemap` | HttpHeaders no longer extends MultiValueMap |
| 4 | `elasticsearch-rest5client` | RestClient → Rest5Client rename |
| 5 | `entityscan-relocated` | @EntityScan moved to persistence.autoconfigure |
| 6 | `propertymapping-relocated` | @PropertyMapping annotation moved |
| 7 | `kafka-streams-customizer-removed` | StreamBuilderFactoryBeanCustomizer → StreamsBuilderFactoryBeanConfigurer |
| 8 | `aop-starter-rename` | spring-boot-starter-aop → spring-boot-starter-aspectj |
| 9 | `simpdest-message-matcher-removed` | Spring Security messaging matcher removed |
| 10 | `apacheds-ldap-removed` | ApacheDS embedded LDAP support removed |
| 11 | `spring-security-access-relocated` | Access API moved to spring-security-access module |
| 12 | `propertymapper-alwaysapplyingnonnull` | PropertyMapper.alwaysApplyingWhenNonNull() removed |
| 13 | `httpcomponents-setconnecttimeout-removed` | setConnectTimeout method removed |
| 14 | `hibernate-query-setorder-removed` | Query#setOrder removed |
| 15 | `hibernate-empty-interceptor-removed` | EmptyInterceptor removed |
| 16 | `hibernate-where-orderby-removed` | @Where and @OrderBy removed |
| 17 | `batch-job-builder-string-constructor` | JobBuilder(String) constructor removed |
| 18 | `batch-package-moves` | org.springframework.batch.core.* package relocations |
| 19 | `batch-chunkhandler-renamed` | ChunkHandler → ChunkRequestHandler |
| 20 | `actuator-nullable-removed` | Actuator endpoint params can't use org.springframework.lang.Nullable |

---

## On hold (1)

- **`webjars-locator-core-removed`** — marked `[!]` in TODO.md; no primary source evidence found in Boot 4.0 Migration Guide or Release Notes. Do not create a card until a verbatim source quote is found.

---

## Already covered (16)

jackson-group-id, undertow-removed, security-removed-apis (×2 cards), hibernate-session-delete,
hibernate-cascade-removal, testcontainers-class-relocation, spring-retry-removed,
hibernate-processor-rename, listenable-future-removed, okhttp3-removed, spring-jcl-removed,
aspectj-observed, retry-semantics-change, retryable-transaction-order, path-matching-engine,
jackson-property-inclusion
