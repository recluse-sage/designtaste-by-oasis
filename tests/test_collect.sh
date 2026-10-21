#!/usr/bin/env bash
# Task 3: from sample answers + 2 links, collect.py outputs ranked-parts.json
# covering all fixed parts (with fallback to curated-defaults.md on fetch fail).
set -u
BASE="$(cd "$(dirname "$0")/.." && pwd)"
SKILL="$BASE/skills/designtaste-by-oasis"
SCRIPT="$SKILL/scripts/collect.py"
QNR="$SKILL/references/questionnaire.md"
DEFAULTS="$SKILL/assets/curated-defaults.md"
PASS=0; FAIL=0

ok()  { echo "PASS: $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL: $1"; FAIL=$((FAIL+1)); }

if [ ! -f "$SCRIPT" ]; then
  bad "missing scripts/collect.py"
  echo "---"
  echo "passed=$PASS failed=$FAIL"
  echo "RESULT: FAIL"
  exit 1
fi
ok "exists scripts/collect.py"

if [ -f "$QNR" ]; then ok "exists references/questionnaire.md"; else bad "missing references/questionnaire.md"; fi
if [ -f "$DEFAULTS" ]; then ok "exists assets/curated-defaults.md"; else bad "missing assets/curated-defaults.md"; fi

if [ -f "$DEFAULTS" ]; then
  COUNT=$(grep -c '^## ' "$DEFAULTS" 2>/dev/null || true)
  if [ "$COUNT" -ge 6 ] && [ "$COUNT" -le 8 ]; then
    ok "curated-defaults.md has $COUNT defaults (6-8)"
  else
    bad "curated-defaults.md has $COUNT defaults (expected 6-8)"
  fi
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/answers.json" <<'EOF'
{
  "answers": {
    "q1": "airy, sharp, calm",
    "q2": "founders; book a demo",
    "q3": "calm and trustworthy, bold only in hero",
    "q4": "no gradients, keep existing logo",
    "q5": "hero matters most"
  },
  "liked": ["http://127.0.0.1:9/liked-one", "http://127.0.0.1:9/liked-two"],
  "disliked": {"url": "http://127.0.0.1:9/disliked", "why": "cluttered and loud"}
}
EOF
OUT="$TMP/ranked-parts.json"

# Unreachable localhost URLs force the curated-defaults fallback path (no network needed).
if python3 "$SCRIPT" --input "$TMP/answers.json" --output "$OUT" 2>"$TMP/stderr.txt"; then
  ok "collect.py exits 0"
else
  bad "collect.py exits non-zero"
fi

if [ -f "$OUT" ]; then ok "ranked-parts.json written"; else bad "ranked-parts.json missing"; fi

if python3 - "$OUT" <<'EOF' 2>/dev/null; then
import json, sys
parts = ["sections", "buttons", "modals", "backgrounds", "color",
         "3D", "animation", "forms", "aesthetic", "arrangement"]
data = json.load(open(sys.argv[1]))
recs = data if isinstance(data, list) else data.get("parts", [])
by_part = {r.get("part"): r for r in recs if isinstance(r, dict)}
missing = [p for p in parts if p not in by_part]
bad_recs = [p for p, r in by_part.items()
            if not r.get("example") or not r.get("verdict")]
assert not missing, f"missing parts: {missing}"
assert not bad_recs, f"empty example/verdict: {bad_recs}"
print(f"ok: all {len(parts)} fixed parts covered with example + verdict")
EOF
  ok "ranked-parts.json valid JSON covering all fixed parts"
else
  bad "ranked-parts.json invalid or missing fixed parts"
fi

echo "---"
echo "passed=$PASS failed=$FAIL"
[ "$FAIL" -eq 0 ]
