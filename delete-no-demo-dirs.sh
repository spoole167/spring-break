#!/usr/bin/env bash
# Delete unwired directories that don't demonstrate a 3.5→4.0 breaking change.
# Verdicts from the 15 July 2026 retest (see REVIEW-FINDINGS.md).
# Uses git rm so the deletions are staged; review with `git status` before committing.
set -euo pipefail
cd "$(dirname "$0")"

# ── No demo: tests pass on BOTH 3.5.16 and 4.0.7 ────────────────────
NO_DEMO=(
  batch-static-meterregistry-removed
  jersey-jackson2-required
  modular-starters
  obs-junit4-vintage-removed
  obs-reactor-take-prefetch
  springextension-method-scope     # already documented as dropped (TODO.md row 2.14)
)

# ── Duplicate: works, but same demo as the wired javax-inject-removed ──
DUPLICATE=(
  obs-javax-inject-removed
)

# ── Borderline — uncomment to delete these too ──────────────────────
# Broken on the 3.5.16 baseline (delete, or fix if the change deserves a demo):
#   obs-config-props-field-binding             # @ConstructorBinding symbol absent on 3.5
#   obs-httpcomponents-setconnecttimeout-removed  # calls HttpClient5 method absent on 3.5
#   obs-like-pattern-escaping                  # premise already false on 3.5.16
# Empty shells (delete, or finish):
#   resttemplatebuilder-settimeout-removed     # 0-byte pom, no tests
#   webclient-system-proxy-optin               # pom only, no source
BORDERLINE=(
)

# NOT deleted: cors-empty-config-not-rejected — fails on 4.0.7 for the wrong
# reason (@AutoConfigureMockMvc relocation, not the advertised CORS change).
# Worth reworking rather than removing.

for dir in "${NO_DEMO[@]}" "${DUPLICATE[@]}" ${BORDERLINE[@]+"${BORDERLINE[@]}"}; do
  if [ -d "$dir" ]; then
    git rm -r --quiet "$dir" 2>/dev/null || true
    rm -rf "$dir"   # catches untracked leftovers (target/, .DS_Store)
    echo "deleted: $dir"
  else
    echo "already gone: $dir"
  fi
done

echo
echo "Staged deletions — review with: git status"
echo "Commit with: git commit -m 'Remove directories that do not demonstrate a 3.5->4.0 break'"
