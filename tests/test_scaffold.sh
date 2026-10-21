#!/usr/bin/env bash
# Task 1 scaffold test: SKILL.md exists, name matches folder, description non-empty, body <500 lines.
set -u
SKILL="skills/designtaste-by-oasis/SKILL.md"
FAIL=0

cd "$(dirname "$0")/.." || exit 1

if [[ ! -f "$SKILL" ]]; then
  echo "FAIL: missing $SKILL"
  exit 1
fi
echo "ok: $SKILL exists"

# Extract frontmatter (between first two --- lines)
NAME=$(awk '/^---$/{n++; next} n==1 && /^name:[[:space:]]*/{sub(/^name:[[:space:]]*/, ""); print; exit}' "$SKILL")
DESC=$(awk '/^---$/{n++; next} n==1 && /^description:[[:space:]]*/{sub(/^description:[[:space:]]*/, ""); print; exit}' "$SKILL")

if [[ -z "${NAME:-}" ]]; then
  echo "FAIL: frontmatter name is empty"
  FAIL=1
else
  echo "ok: name=$NAME"
fi

FOLDER=$(basename "$(dirname "$SKILL")")
if [[ "$NAME" != "$FOLDER" ]]; then
  echo "FAIL: name '$NAME' does not match folder '$FOLDER'"
  FAIL=1
else
  echo "ok: folder matches name"
fi

if [[ ! "$NAME" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "FAIL: name violates regex ^[a-z0-9]+(-[a-z0-9]+)*$"
  FAIL=1
fi

if [[ -z "${DESC:-}" ]]; then
  echo "FAIL: frontmatter description is empty"
  FAIL=1
else
  echo "ok: description non-empty (${#DESC} chars)"
  if (( ${#DESC} > 1024 )); then
    echo "FAIL: description exceeds 1024 chars"
    FAIL=1
  fi
fi

# Body = everything after the second --- line; must be <500 lines
BODY_LINES=$(awk '/^---$/{n++; if (n==2) {start=NR; next}} n>=2 {c++} END{print c+0}' "$SKILL")
if [[ "$BODY_LINES" -ge 500 ]]; then
  echo "FAIL: body is $BODY_LINES lines (>=500)"
  FAIL=1
else
  echo "ok: body $BODY_LINES lines (<500)"
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "RESULT: FAIL"
  exit 1
fi
echo "RESULT: PASS"
