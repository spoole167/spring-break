#!/usr/bin/env bash
# Produce every edition declared in cards/pagewright.yaml (publication: block):
# the full guide, the nine per-stack mini guides, and the heavy-hitters cut.
# Output lands in dist/.
#
# Usage:
#   ./publish.sh                       # all editions, Chromium renderer
#   ./publish.sh batch-guide           # one edition (any declared ids)
#   RENDERER=openhtmltopdf ./publish.sh    # pure-Java fallback renderer
#   ./publish.sh --set defaults.theme=console-first hibernate-guide   # experiments
#
# The edition list, themes, sizes, selections and page contracts all live in
# cards/pagewright.yaml — this script is deliberately just "find the jar,
# run publish". Anything you'd edit here twice belongs in that yaml.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PAGEWRIGHT_REPO="${PAGEWRIGHT_REPO:-$HOME/claude_projects/pagewright}"
JAR="$PAGEWRIGHT_REPO/pagewright-cli/target/pagewright-cli-0.1.0-SNAPSHOT-all.jar"
RENDERER="${RENDERER:-playwright}"

# ── jar: build if missing, rebuild if sources are newer ─────────────────────
if [ ! -f "$JAR" ]; then
  echo "publish: jar not found — building pagewright..."
  (cd "$PAGEWRIGHT_REPO" && mvn -q -DskipTests package)
elif [ -n "$(find "$PAGEWRIGHT_REPO" -name '*.java' -newer "$JAR" -print -quit 2>/dev/null)" ]; then
  echo "publish: sources newer than jar — rebuilding pagewright..."
  (cd "$PAGEWRIGHT_REPO" && mvn -q -DskipTests package)
fi

# ── publish ──────────────────────────────────────────────────────────────────
cd "$ROOT"
java -jar "$JAR" publish -r "$RENDERER" cards "$@"

echo ""
echo "publish: done → $ROOT/dist/"
ls -lh "$ROOT/dist/" | awk 'NR>1 {printf "  %-36s %s\n", $9, $5}'
