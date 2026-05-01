#!/usr/bin/env bash
# Standard build entry point for noregressions guide repos.
#
# Reads guide.json, sets up a Python venv, then runs:
#   1. generate.py  → target/pdfs/  (per-card PDFs + merged guide.pdf)
#   2. build-site.py → target/site/ (static HTML site)
#
# Outputs:
#   target/site/   — drop-in static site
#   target/pdfs/   — downloadable PDFs
#
# Usage:
#   ./build.sh           # full build (HTML + PDF)
#   ./build.sh --html    # site only, skip PDFs

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT/.venv"

# ── dependency check ──────────────────────────────────────────────────────────
if [ ! -f "$ROOT/guide.json" ]; then
  echo "build: guide.json not found" >&2
  exit 1
fi

# ── set up venv ───────────────────────────────────────────────────────────────
if [ ! -d "$VENV" ]; then
  echo "build: creating venv..."
  python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"

echo "build: installing dependencies..."
pip install --quiet -r "$ROOT/requirements.txt"

# ── clean previous output ─────────────────────────────────────────────────────
rm -rf "$ROOT/target"
mkdir -p "$ROOT/target/site" "$ROOT/target/pdfs"

# ── build site ────────────────────────────────────────────────────────────────
echo ""
echo "── Building site → target/site/"
python "$ROOT/build-site.py" --out "$ROOT/target/site"

# ── build PDFs (unless --html flag passed) ────────────────────────────────────
if [[ "${1:-}" != "--html" ]]; then
  echo ""
  echo "── Building PDFs → target/pdfs/"
  python "$ROOT/generate.py"
fi

echo ""
echo "build: done."
echo "  site  → target/site/"
echo "  pdfs  → target/pdfs/"
