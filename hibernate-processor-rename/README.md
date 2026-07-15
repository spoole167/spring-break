# Hibernate JPA metamodel generator renamed to hibernate-processor (Tier 1: Won't Resolve)

**Summary**: Hibernate 7 (the ORM behind Spring Boot 4.0) renamed its JPA static metamodel annotation processor from `hibernate-jpamodelgen` to `hibernate-processor`. Builds that declare `org.hibernate.orm:hibernate-jpamodelgen` without a version, relying on the Boot BOM to supply one, fail at dependency resolution on Boot 4.0 because the 4.0 BOM no longer manages that artifact. The build stops before a single line of code is compiled.

## What breaks

In Spring Boot 3.5, the BOM manages the processor version, so this works:

```xml
<dependency>
    <groupId>org.hibernate.orm</groupId>
    <artifactId>hibernate-jpamodelgen</artifactId>
    <scope>provided</scope>
</dependency>
```

In Spring Boot 4.0, the BOM manages `hibernate-processor` instead, so resolution fails:

```
'dependencies.dependency.version' for org.hibernate.orm:hibernate-jpamodelgen:jar is missing
```

The `org.hibernate.orm:hibernate-jpamodelgen` version is missing from the 4.0 BOM because the artifact was renamed to `hibernate-processor` in Hibernate 7.

## How this test works

The pom declares `hibernate-jpamodelgen` twice, both times without a version: once as a `provided` dependency and once in the compiler plugin's `annotationProcessorPaths`. `Product` is a plain JPA `@Entity` with `id`, `name` and `price` fields. During compilation the processor generates the static metamodel class `Product_`. `HibernateProcessorRenameTest.metamodelClassShouldBeGenerated()` loads `com.example.Product_` via `Class.forName` and asserts it exists, proving the processor actually ran.

- On Boot 3.5.16: compiles and passes.
- On Boot 4.0.7: fails at dependency resolution, `org.hibernate.orm:hibernate-jpamodelgen` version missing from the 4.0 BOM. Verified 15 July 2026.

## Fix / Migration Path

Swap the artifact ID in both places (the dependency and the `annotationProcessorPaths` entry):

```xml
<dependency>
    <groupId>org.hibernate.orm</groupId>
    <artifactId>hibernate-processor</artifactId>
    <scope>provided</scope>
</dependency>
```

The generated metamodel classes keep the same names, so no source changes are needed. Note the trap for teams that pin an explicit `hibernate-jpamodelgen` version instead: resolution succeeds, but they silently keep running the old Hibernate 6 processor against Hibernate 7.
