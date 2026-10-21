#!/usr/bin/env bash
# Task 2: asserts all 5 refs exist and SKILL.md links each with one-level relative path.
set -u
BASE="$(cd "$(dirname "$0")/.." && pwd)"
SKILL="$BASE/skills/designtaste-by-oasis/SKILL.md"
REFDIR="$BASE/skills/designtaste-by-oasis/references"
PASS=0; FAIL=0

ok()   { echo "PASS: $1"; PASS=$((PASS+1)); }
bad()  { echo "FAIL: $1"; FAIL=$((FAIL+1)); }

for f in brainstorm-gate.md layout.md taste.md buttons.md copy-slim.md questionnaire.md; do
  if [ -f "$REFDIR/$f" ]; then ok "exists references/$f"; else bad "missing references/$f"; fi
done

if [ -f "$SKILL" ]; then ok "SKILL.md exists"; else bad "SKILL.md missing"; fi

for f in brainstorm-gate.md layout.md taste.md buttons.md copy-slim.md questionnaire.md; do
  # One-level relative path: exactly "references/<file>" (no leading ./ or / and no deeper nesting)
  if grep -q "(references/$f)" "$SKILL" 2>/dev/null; then ok "SKILL.md links references/$f"; else bad "SKILL.md missing link (references/$f)"; fi
done

echo "---"
echo "passed=$PASS failed=$FAIL"
[ "$FAIL" -eq 0 ]
