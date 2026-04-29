#!/bin/bash
# run-all-tests.sh
# Run Maven tests across Spring Boot migration test modules, organised by
# the type of breakage they demonstrate.
#
# Usage:
#   ./run-all-tests.sh                        # 3.5.14 baseline — every module should pass
#   ./run-all-tests.sh -v 4.0.6              # 4.0 target  — every module should FAIL
#   ./run-all-tests.sh -q                    # quiet mode  (summary + failures only)
#   ./run-all-tests.sh module1 module2       # run a subset
#   ./run-all-tests.sh -v 4.0.2 -q          # combine flags
#
# Categories:
#   (a) Won't Compile     — source/deps that exist on 3.5 are missing on 4.0
#   (c) Runtime Errors    — compiles on both versions, throws at runtime on 4.0
#   (d) Different Results — runs on both, but produces different output on 4.0

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

QUIET=0
BOOT_VERSION=""
ARGS=()

while [ $# -gt 0 ]; do
  case "$1" in
    -q|--quiet) QUIET=1; shift ;;
    -v|--version)
      shift
      BOOT_VERSION="${1:-}"
      [ -z "$BOOT_VERSION" ] && { echo "ERROR: -v requires a version (e.g. -v 4.0.2)" >&2; exit 1; }
      shift
      ;;
    -h|--help)
      sed -n '2,16p' "$0"
      exit 0
      ;;
    *) ARGS+=("$1"); shift ;;
  esac
done

if ! command -v mvn >/dev/null 2>&1; then
  echo "ERROR: mvn not found on PATH. Install Maven and retry." >&2
  exit 127
fi

# ── Category definitions ──────────────────────────────────────────────
#
# (a) Won't Compile: real imports / dependencies that vanish on 4.0.
#     On 4.0 the script runs "mvn compile" and EXPECTS failure.
CATEGORY_A=(
  jackson-group-id
  jackson-class-renames
  undertow-removed
  security-removed-apis
  deprecated-classes-removed
  hibernate-session-delete
  hibernate-cascade-removal
  testcontainers-class-relocation
  spring-retry-removed
  hibernate-processor-rename
  listenable-future-removed
  okhttp3-removed
  spring-jcl-removed
  aspectj-observed
  retry-semantics-change
  retryable-transaction-order
  path-matching-engine
  jackson-property-inclusion
  bootstrap-registry-relocated
  testrest-template-removed
  httpheaders-multivaluemap
  elasticsearch-rest5client
  entityscan-relocated
  propertymapping-relocated
  kafka-streams-customizer-removed
  aop-starter-rename
  simpdest-message-matcher-removed
  apacheds-ldap-removed
  spring-security-access-relocated
  propertymapper-alwaysapplyingnonnull
  hibernate-query-setorder-removed
  hibernate-empty-interceptor-removed
  hibernate-where-orderby-removed
  batch-job-builder-string-constructor
  batch-package-moves
  batch-chunkhandler-renamed
  batch-listener-classes
  webjars-locator-core-removed
)

# (c) Runtime Errors: compiles on both versions, but throws at runtime on 4.0.
CATEGORY_C=(
  hibernate-query-type-required
  jackson-exception-hierarchy
  hibernate-dialect-removal
  oauth-password-grant-removed
  mockbean-removed
  batch-schema-change
  batch-job-serialisation
  pkce-mandatory
  opensaml4-removed
  resttemplate-autoconfig
  test-slice-relocated
  mockito-test-execution-listener
  javax-annotation-removed
  javax-inject-removed
  actuator-nullable-removed
)

# (d) Different Results: runs on both, assertions detect different behaviour.
CATEGORY_D=(
  jackson-date-serialisation
  jackson-dates-timestamps
  jackson-locale-format
  hibernate-native-datetime
)

# Portable category lookup (works on bash 3.x / macOS)
module_cat() {
  local mod="$1"
  for m in "${CATEGORY_A[@]}"; do [ "$m" = "$mod" ] && echo "a" && return; done
  for m in "${CATEGORY_C[@]}"; do [ "$m" = "$mod" ] && echo "c" && return; done
  for m in "${CATEGORY_D[@]}"; do [ "$m" = "$mod" ] && echo "d" && return; done
  echo "?"
}

# Detect whether target version is 4.x
IS_4X=0
if [[ -n "$BOOT_VERSION" && "$BOOT_VERSION" == 4* ]]; then
  IS_4X=1
fi

# Module list — explicit args override the defaults
if [ ${#ARGS[@]} -gt 0 ]; then
  MODULES=("${ARGS[@]}")
else
  MODULES=("${CATEGORY_A[@]}" "${CATEGORY_C[@]}" "${CATEGORY_D[@]}")
fi

if [ ${#MODULES[@]} -eq 0 ]; then
  echo "No modules to run." >&2
  exit 1
fi

# ── ANSI colours ──────────────────────────────────────────────────────
if [ -t 1 ]; then
  GREEN=$'\033[32m'; RED=$'\033[31m'; YELLOW=$'\033[33m'; CYAN=$'\033[36m'
  BOLD=$'\033[1m'; DIM=$'\033[2m'; RESET=$'\033[0m'
else
  GREEN=""; RED=""; YELLOW=""; CYAN=""; BOLD=""; DIM=""; RESET=""
fi

LOG_DIR="$SCRIPT_DIR/.test-logs"
mkdir -p "$LOG_DIR"

VERSION_FLAG=""
[ -n "$BOOT_VERSION" ] && VERSION_FLAG="-Dspring-boot.version=$BOOT_VERSION"

PASSED=()
FAILED=()
START_TS=$(date +%s)

VERSION_LABEL="${BOOT_VERSION:-3.5.14 (default)}"

# ── Banner ────────────────────────────────────────────────────────────
printf "\n%s━━━ Spring Boot 3.5 → 4.0 Migration Test Suite ━━━%s\n" "$BOLD" "$RESET"
printf "  Spring Boot : %s\n" "$VERSION_LABEL"
printf "  Modules     : %d\n\n" "${#MODULES[@]}"
printf "  %s(a)%s Won't Compile      %s(c)%s Runtime Errors      %s(d)%s Different Results\n" \
  "$CYAN" "$RESET" "$CYAN" "$RESET" "$CYAN" "$RESET"

# ── Run each module ──────────────────────────────────────────────────
current_cat=""

for module in "${MODULES[@]}"; do
  if [ ! -f "$module/pom.xml" ]; then
    printf "  %s[SKIP]%s %s (no pom.xml)\n" "$YELLOW" "$RESET" "$module"
    continue
  fi

  cat="$(module_cat "$module")"

  # Print a category header when the category changes
  if [ "$cat" != "$current_cat" ]; then
    current_cat="$cat"
    case "$cat" in
      a) printf "\n%sCategory (a) — Won't Compile%s\n" "$BOLD" "$RESET" ;;
      c) printf "\n%sCategory (c) — Runtime Errors%s\n" "$BOLD" "$RESET" ;;
      d) printf "\n%sCategory (d) — Different Results%s\n" "$BOLD" "$RESET" ;;
      *) printf "\n%sUncategorized%s\n" "$BOLD" "$RESET" ;;
    esac
  fi

  # Category (a) on 4.x → compile-only (tests won't even compile)
  # BUT some modules in CATEGORY_A might actually fail at test execution (runtime)
  # even if they are categorized as (a) because they use reflection or are Tier 2 style.
  # We force CATEGORY_A to compile only on 4.x to catch Tier 1 breaks.
  if [ "$cat" = "a" ] && [ "$IS_4X" -eq 1 ]; then
    if false; then
      # (placeholder — no CATEGORY_A runtime-only special cases currently)
      GOAL="clean test"
    else
      GOAL="clean compile test-compile"
    fi
  else
    GOAL="clean test"
  fi

  MVN_CMD="mvn -B $GOAL $VERSION_FLAG"

  printf "  [....] %s" "$module"
  log="$LOG_DIR/${module}.log"

  if [ "$QUIET" -eq 1 ]; then
    ( cd "$module" && eval $MVN_CMD ) >"$log" 2>&1
    rc=$?
  else
    ( cd "$module" && eval $MVN_CMD ) 2>&1 | tee "$log" >/dev/null
    rc=${PIPESTATUS[0]}
  fi

  if [ $rc -eq 0 ]; then
    printf "\r  %s[PASS]%s %s\n" "$GREEN" "$RESET" "$module"
    PASSED+=("$module")
  else
    printf "\r  %s[FAIL]%s %s  %s→ .test-logs/%s.log%s\n" "$RED" "$RESET" "$module" "$DIM" "$module" "$RESET"
    FAILED+=("$module")
  fi
done

END_TS=$(date +%s)
ELAPSED=$(( END_TS - START_TS ))

# ── Summary ──────────────────────────────────────────────────────────
printf "\n%s━━━ Summary ━━━%s  [Boot %s]  %ds\n" "$BOLD" "$RESET" "$VERSION_LABEL" "$ELAPSED"
printf "  %sPassed:%s %d    %sFailed:%s %d    Total: %d\n" \
  "$GREEN" "$RESET" "${#PASSED[@]}" \
  "$RED" "$RESET" "${#FAILED[@]}" \
  "$(( ${#PASSED[@]} + ${#FAILED[@]} ))"

if [ ${#FAILED[@]} -gt 0 ]; then
  printf "\n  Failed:\n"
  for m in "${FAILED[@]}"; do
    printf "    %s✗%s (%s) %s\n" "$RED" "$RESET" "$(module_cat "$m")" "$m"
  done
fi

# On 4.x, passing is the surprise — flag it
if [ "$IS_4X" -eq 1 ] && [ ${#PASSED[@]} -gt 0 ]; then
  printf "\n  %s⚠  Unexpected passes on 4.x — these tests may not be catching the break:%s\n" "$YELLOW" "$RESET"
  for m in "${PASSED[@]}"; do
    printf "    %s?%s (%s) %s\n" "$YELLOW" "$RESET" "$(module_cat "$m")" "$m"
  done
fi

printf "\n  Logs: .test-logs/\n\n"

# Exit code:
#   3.x → 0 if all pass, 1 if any fail
#   4.x → 0 if all fail (expected), 1 if any pass unexpectedly
if [ "$IS_4X" -eq 1 ]; then
  [ ${#PASSED[@]} -eq 0 ] && exit 0 || exit 1
else
  [ ${#FAILED[@]} -eq 0 ] && exit 0 || exit 1
fi
