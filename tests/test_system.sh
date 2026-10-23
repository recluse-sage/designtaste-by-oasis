#!/usr/bin/env bash
# Task 5: from sample feedback, the DESIGN-SYSTEM-TEMPLATE.md renders a
# design-system.md with tokens-not-values, all states, layout,
# breakpoints, animation notes, plus the check-ask-update rule text.
set -u
BASE="$(cd "$(dirname "$0")/.." && pwd)"
SKILL="$BASE/skills/designtaste-by-oasis"
WRITER="$SKILL/references/system-writer.md"
TEMPLATE="$BASE/DESIGN-SYSTEM-TEMPLATE.md"
INSKILL="$SKILL/assets/DESIGN-SYSTEM-TEMPLATE.md"
README="$BASE/README.md"
SKILLMD="$SKILL/SKILL.md"
PASS=0; FAIL=0

ok()  { echo "PASS: $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL: $1"; FAIL=$((FAIL+1)); }

# --- File existence. ---
if [ ! -f "$WRITER" ]; then
  bad "missing references/system-writer.md"
  echo "---"
  echo "passed=$PASS failed=$FAIL"
  echo "RESULT: FAIL"
  exit 1
fi
ok "exists references/system-writer.md"

if [ ! -f "$TEMPLATE" ]; then
  bad "missing DESIGN-SYSTEM-TEMPLATE.md"
  echo "---"
  echo "passed=$PASS failed=$FAIL"
  echo "RESULT: FAIL"
  exit 1
fi
ok "exists DESIGN-SYSTEM-TEMPLATE.md"

if [ -f "$INSKILL" ]; then
  ok "exists skills/designtaste-by-oasis/assets/DESIGN-SYSTEM-TEMPLATE.md"
else
  bad "missing skills/designtaste-by-oasis/assets/DESIGN-SYSTEM-TEMPLATE.md"
fi

# --- system-writer.md contract: picked direction + feedback in, system out. ---
for needle in 'design-feedback.md' 'design-system.md' 'picked'; do
  if grep -qF "$needle" "$WRITER"; then ok "system-writer.md mentions '$needle'";
  else bad "system-writer.md missing '$needle'"; fi
done
if grep -qi 'token' "$WRITER"; then ok "system-writer.md covers tokens-not-values";
else bad "system-writer.md missing token rule"; fi
if grep -qi 'check-ask-update' "$WRITER"; then ok "system-writer.md mentions check-ask-update rule";
else bad "system-writer.md missing check-ask-update rule"; fi

# --- SKILL.md router link (one-level relative path). ---
if grep -q '(references/system-writer.md)' "$SKILLMD" 2>/dev/null; then
  ok "SKILL.md links references/system-writer.md"
else
  bad "SKILL.md missing link (references/system-writer.md)"
fi

# --- Required-section checker, reused for template and rendered output. ---
check_sections() { # $1=file $2=label
  local f=$1 label=$2 s
  if grep -qi 'token' "$f" && grep -qi 'not values' "$f"; then
    ok "$label: tokens-not-values section"
  else
    bad "$label: missing tokens-not-values section"
  fi
  for s in default hover active disabled loading error empty; do
    if grep -qi "$s" "$f"; then ok "$label: state '$s'";
    else bad "$label: missing state '$s'"; fi
  done
  if grep -qi 'layout' "$f"; then ok "$label: layout section";
  else bad "$label: missing layout section"; fi
  if grep -qi 'breakpoint' "$f"; then ok "$label: breakpoints section";
  else bad "$label: missing breakpoints section"; fi
  if grep -qi 'animation' "$f"; then ok "$label: animation notes";
  else bad "$label: missing animation notes"; fi
  if grep -qi 'reduced-motion' "$f"; then ok "$label: reduced-motion note";
  else bad "$label: missing reduced-motion note"; fi
  if grep -qi 'check-ask-update' "$f"; then ok "$label: check-ask-update rule text";
  else bad "$label: missing check-ask-update rule text"; fi
}

check_sections "$TEMPLATE" "template"

# --- README install/findability section (appended, existing content kept). ---
if [ -f "$README" ]; then
  for needle in 'visual direction' 'wireframe review' 'design system' 'website taste'; do
    if grep -qiF "$needle" "$README"; then ok "README has keyword '$needle'";
    else bad "README missing keyword '$needle'"; fi
  done
  if grep -q 'skills.sh' "$README"; then ok "README mentions skills.sh";
  else bad "README missing skills.sh"; fi
  if grep -q 'npx skills add' "$README"; then ok "README has npx skills add install";
  else bad "README missing npx skills add install"; fi
else
  bad "README.md missing"
fi

# --- Functional render: sample feedback + picked direction -> design-system.md. ---
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/design-feedback.md" <<'EOF'
# design-feedback - sample
## hero-landing
- verdict: green
- comment: airy hero with one calm CTA keeps focus - sample 4f2a
## pricing-grid
- verdict: red
- comment: too dense, cards collide - sample 9b1c
EOF

PICKED="direction-b"
SUMMARY="hero-landing kept (green); pricing-grid reworked (red) - sample 4f2a"
sed -e "s|{{PROJECT_NAME}}|sample-site|g" \
    -e "s|{{DATE}}|2026-10-21|g" \
    -e "s|{{PICKED_DIRECTION}}|$PICKED|g" \
    -e "s|{{FEEDBACK_SUMMARY}}|$SUMMARY|g" \
  "$TEMPLATE" > "$TMP/design-system.md"

if [ -f "$TMP/design-system.md" ]; then
  ok "template renders design-system.md"
else
  bad "template render produced no design-system.md"
fi

if grep -qF "$PICKED" "$TMP/design-system.md" 2>/dev/null; then
  ok "rendered md records picked direction"
else
  bad "rendered md missing picked direction"
fi
if grep -qF "hero-landing kept (green)" "$TMP/design-system.md" 2>/dev/null; then
  ok "rendered md records feedback summary"
else
  bad "rendered md missing feedback summary"
fi
if grep -q '{{' "$TMP/design-system.md" 2>/dev/null; then
  bad "rendered md has unfilled placeholders"
else
  ok "rendered md has no unfilled placeholders"
fi

check_sections "$TMP/design-system.md" "rendered"

echo "---"
echo "passed=$PASS failed=$FAIL"
if [ "$FAIL" -eq 0 ]; then echo "RESULT: PASS"; else echo "RESULT: FAIL"; fi
[ "$FAIL" -eq 0 ]
