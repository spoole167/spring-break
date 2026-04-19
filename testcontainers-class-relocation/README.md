# Testcontainers Class Relocation (Tier 1: Won't Launch)

**Summary**: Testcontainers 2.0 (in Boot 4.0) relocates database container classes from `org.testcontainers.containers.*` to database-specific packages like `org.testcontainers.postgresql.*`, breaking all import statements.

## What Breaks

Testcontainers 2.0 **relocated** container classes from a monolithic package structure to modular, database-specific packages:

1. **PostgreSQL**: `org.testcontainers.containers.PostgreSQLContainer` → `org.testcontainers.postgresql.PostgreSQLContainer`
2. **MySQL**: `org.testcontainers.containers.MySQLContainer` → `org.testcontainers.mysql.MySQLContainer`
3. **Similar relocations** for all database containers
4. **New module dependencies** required: `testcontainers-postgresql`, `testcontainers-mysql`, etc.
5. **Old imports broken** — all code using old package paths fails to compile

This is a **Tier 1 failure**: compile-time error preventing build.

## How This Test Works

The test module uses reflection to verify container class locations:

- **ContainerRelocationTest.java**: Two tests checking class availability:
  - `postgresContainerShouldBeInOriginalPackage()` — checks old `org.testcontainers.containers.PostgreSQLContainer`
  - `genericContainerShouldBeLoadable()` — checks stable `org.testcontainers.containers.GenericContainer`
- **App.java**: Minimal Spring Boot application

## On Spring Boot 3.4.1 (Testcontainers 1.x)

```bash
mvn clean test
```

**Result**: ✓ Both tests pass. Container classes in old `org.testcontainers.containers.*` packages.

```
[INFO] Tests run: 2, Failures: 0, Errors: 0
[INFO] postgresContainerShouldBeInOriginalPackage ✓
[INFO] genericContainerShouldBeLoadable ✓
```

```bash
mvn clean test
```

**Result**: ✗ First test fails. PostgreSQL container class relocated.

```
[ERROR] postgresContainerShouldBeInOriginalPackage ✗
[ERROR] java.lang.ClassNotFoundException: org.testcontainers.containers.PostgreSQLContainer
```

## Fix / Migration Path

### 1. Update pom.xml with Database-Specific Module

Add the new Testcontainers module for your database:

```xml
<!-- OLD (Testcontainers 1.x) — included in core dependency -->
<dependency>
  <groupId>org.testcontainers</groupId>
  <artifactId>testcontainers</artifactId>
  <scope>test</scope>
</dependency>

<!-- NEW (Testcontainers 2.x) — add database-specific module -->
<dependency>
  <groupId>org.testcontainers</groupId>
  <artifactId>testcontainers</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.testcontainers</groupId>
  <artifactId>postgresql</artifactId>
  <scope>test</scope>
</dependency>
```

### 2. Update Imports

Replace old package paths with database-specific packages:

```java
// OLD (Testcontainers 1.x)
import org.testcontainers.containers.PostgreSQLContainer;

// NEW (Testcontainers 2.x)
import org.testcontainers.postgresql.PostgreSQLContainer;
```

### 3. Update Container Declarations

Update static container declarations and remove generic type parameters:

```java
// OLD
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
    DockerImageName.parse("postgres:15")
);

// NEW
static PostgreSQLContainer postgres = new PostgreSQLContainer(
    DockerImageName.parse("postgres:15")
);
```

### 4. Database-Specific Modules

Common Testcontainers 2.x modules:
- `testcontainers-postgresql` → `org.testcontainers.postgresql.PostgreSQLContainer`
- `testcontainers-mysql` → `org.testcontainers.mysql.MySQLContainer`
- `testcontainers-mongodb` → `org.testcontainers.mongodb.MongoDBContainer`
- `testcontainers-elasticsearch` → `org.testcontainers.elasticsearch.ElasticsearchContainer`
- `testcontainers-mariadb` → `org.testcontainers.mariadb.MariaDBContainer`

## References

- [Testcontainers 2.0 Migration Guide](https://testcontainers.com/guides/testcontainers-2-migration/)
- [Testcontainers 2.0 Changelog](https://github.com/testcontainers/testcontainers-java/releases)
- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)

```bash
mvn clean test -Dspring-boot.version=4.0.2
```

**Expected Output**:
```
[INFO] Tests run: 2, Failures: 1, Errors: 0, Skipped: 0
[ERROR] postgresContainerShouldBeInOriginalPackage — ClassNotFoundException
```

The first test fails because `org.testcontainers.containers.PostgreSQLContainer` no longer exists on the classpath.

## What Breaks on Spring Boot 4.0

When you use the old imports in your application code:

### Example Breaking Code:

```java
import org.testcontainers.containers.PostgreSQLContainer;

@SpringBootTest
class MyDataTests {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
        DockerImageName.parse("postgres:15")
    );

    @Test
    void testWithPostgres() {
        // ...
    }
}
```

### Compilation Error:

```
error: package org.testcontainers.containers does not exist
import org.testcontainers.containers.PostgreSQLContainer;
```

## The Fix

Update your code and pom.xml to use Testcontainers 2.0 APIs:

### 1. Update pom.xml

Add database-specific modules:
```xml
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <scope>test</scope>
</dependency>
```

### 2. Update Imports

```java
// OLD (Testcontainers 1.x)
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.containers.DockerImageName;

// NEW (Testcontainers 2.x)
import org.testcontainers.postgresql.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
```

### 3. Update Container Usage

```java
// OLD
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
    DockerImageName.parse("postgres:15")
);

// NEW
static PostgreSQLContainer postgres = new PostgreSQLContainer(
    DockerImageName.parse("postgres:15")
);
```

### 4. Supported Database Modules in Testcontainers 2.0

- `org.testcontainers:postgresql`
- `org.testcontainers:mysql`
- `org.testcontainers:mariadb`
- `org.testcontainers:mongodb`
- `org.testcontainers:elasticsearch`
- And many others...

Each comes with its specific container class in the dedicated package.

## Migration Checklist

- [ ] Review all `org.testcontainers.containers.*` imports in your test code
- [ ] Identify which database modules you use
- [ ] Add corresponding Testcontainers modules to pom.xml
- [ ] Update all imports to new database-specific packages
- [ ] Update container class declarations (e.g., remove generic `<?>`)
- [ ] Run `mvn clean test` to verify
- [ ] Test container startup and connectivity
