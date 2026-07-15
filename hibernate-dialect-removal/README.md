# Hibernate Version-Specific Dialects Removed (Tier 1: Won't Compile)

Version-specific database dialects removed in Hibernate 7.0; use auto-detection or generic dialects.

## What Breaks

Hibernate 7.0 (Spring Boot 4.0) removes all version-specific dialect classes. Any Java code that references one of these classes stops compiling.

**Removed dialects (Hibernate 7.0):**
- MySQL57Dialect, MySQL8Dialect
- PostgreSQL96Dialect, PostgreSQL10Dialect, PostgreSQL11Dialect
- Oracle10gDialect, Oracle12cDialect
- SQLServer2008Dialect, SQLServer2012Dialect
- And many others (all version-specific variants)

**Measured on Spring Boot 4.0.7 (clean build):**
```
[ERROR] cannot find symbol: class MySQL8Dialect
```

This module references the dialect class directly in Java, so the removal shows up at compile time.

**The runtime variant matters more in practice.** Most real applications never touch a dialect class in Java. They name it as a string in configuration:
```properties
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQL8Dialect
```
That kind of application compiles cleanly on 4.0 and then fails at startup with `ClassNotFoundException: org.hibernate.dialect.MySQL8Dialect`. Same removal, different failure point. This module demonstrates the compile-time variant; if your dialect lives in application.properties, expect the runtime one.

Hibernate 7.0 auto-detects the database dialect from JDBC driver metadata, making explicit dialect configuration unnecessary in most cases.

## How This Test Works

The test combines CRUD operations with a direct class reference:

- **testCreateAndRetrieveProduct()** / **testFindProductById()**: Verify basic JPA operations work with the auto-detected dialect (H2 in-memory database).
- **versionSpecificDialectClassShouldBeLoadable()**: References `MySQL8Dialect.class` directly. The import alone is enough: on Hibernate 6.x the class exists (deprecated), on Hibernate 7.0 it is gone and the test source no longer compiles.

Verified 15 July 2026.

## On Spring Boot 3.5.16

```bash
mvn clean test
```

Output: All tests pass. Version-specific dialects exist and are loadable.

## On Spring Boot 4.0.7

Compilation of the test sources fails:
```
[ERROR] cannot find symbol: class MySQL8Dialect
```

No tests run. An application that instead configures a version-specific dialect in application.properties would compile, then fail to start with `ClassNotFoundException`.

## Fix / Migration Path

**Option 1: Remove explicit dialect (recommended)**

Delete any lines like these from application.properties:
```properties
# REMOVE:
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQL57Dialect
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQL10Dialect
```

Hibernate auto-detects from the JDBC driver:
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/mydb
spring.datasource.driverClassName=com.mysql.cj.jdbc.Driver
# No explicit dialect needed: Hibernate detects MySQL automatically
```

**Option 2: Use generic (version-agnostic) dialects**

If you must specify a dialect:
```properties
# Generic dialects that work across major versions:
spring.jpa.database-platform=org.hibernate.dialect.MySQLDialect
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect
spring.jpa.database-platform=org.hibernate.dialect.OracleDialect
spring.jpa.database-platform=org.hibernate.dialect.SQLServerDialect
```

**Audit and migrate:**
```bash
# Find all explicit dialect configurations
grep -r "hibernate\.dialect" src/main/resources/
# Find direct class references in Java
grep -rn "Dialect" src/main/java/ src/test/java/
# Remove version-specific ones; replace with generic or remove entirely
```

## References

- Hibernate 7.0 Migration Guide: https://docs.jboss.org/hibernate/orm/7.0/migration-guide/migration-guide.html
- Hibernate ORM 7.0 Release: https://docs.hibernate.org/orm/7.0/migration-guide/migration-guide.html
- Spring Boot 4.0 Migration Guide: https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
