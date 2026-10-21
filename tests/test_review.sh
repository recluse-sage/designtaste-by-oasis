#!/usr/bin/env bash
# Task 4: review server + feedback persistence.
# Starts serve.py, POSTs sample red/green + text for one section, asserts
# design-feedback.md contains the section id + verdict + comment.
set -u
BASE="$(cd "$(dirname "$0")/.." && pwd)"
SKILL="$BASE/skills/designtaste-by-oasis"
SERVE="$SKILL/scripts/serve.py"
SAVE="$SKILL/scripts/save_feedback.py"
PASS=0; FAIL=0

ok()  { echo "PASS: $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL: $1"; FAIL=$((FAIL+1)); }

if [ ! -f "$SERVE" ]; then
  bad "missing scripts/serve.py"
  echo "---"
  echo "passed=$PASS failed=$FAIL"
  echo "RESULT: FAIL"
  exit 1
fi
ok "exists scripts/serve.py"

if [ ! -f "$SAVE" ]; then
  bad "missing scripts/save_feedback.py"
  echo "---"
  echo "passed=$PASS failed=$FAIL"
  echo "RESULT: FAIL"
  exit 1
fi
ok "exists scripts/save_feedback.py"

# Static contract checks (spec Sections 3-5).
grep -q '8000' "$SERVE" || bad "serve.py does not mention default port 8000"
grep -qi 'busy' "$SERVE" || bad "serve.py has no busy-port handling"
grep -q -i 'next free port' "$SERVE" || bad "serve.py has no next-free-port fallback"
grep -q -i 'red' "$SERVE" && grep -q -i 'green' "$SERVE" \
  && ok "serve.py has red/green review UI" \
  || bad "serve.py missing red/green review UI"
grep -q 'textarea' "$SERVE" || bad "serve.py review UI has no text box"
grep -q '/save' "$SERVE" || bad "serve.py has no /save hook"
grep -q 'design-feedback.md' "$SAVE" || bad "save_feedback.py does not target design-feedback.md"
grep -qi 'download' "$SAVE" || bad "save_feedback.py has no download fallback"
if [ "$FAIL" -eq 0 ]; then ok "static contract checks"; fi

free_port() {
  python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()'
}

wait_for() { # $1=url [$2=tries]
  local url=$1 n=${2:-50} i=0
  while [ "$i" -lt "$n" ]; do
    if curl -s -o /dev/null --max-time 1 "$url" 2>/dev/null; then return 0; fi
    sleep 0.2; i=$((i+1))
  done
  return 1
}

TMP="$(mktemp -d)"
PIDS=""
cleanup() {
  for p in $PIDS; do
    [ -n "$p" ] && kill "$p" 2>/dev/null
  done
  wait 2>/dev/null || true
  rm -rf "$TMP"
}
trap cleanup EXIT

DOCROOT="$TMP/wireframes"
mkdir -p "$DOCROOT"

# --- Busy-port fallback: occupy a port, server must surface a new URL. ---
BUSY="$(free_port)"
python3 - "$BUSY" <<'EOF' &
import socket, sys, time
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", int(sys.argv[1])))
s.listen(1)
time.sleep(25)
EOF
PIDS="$PIDS $!"
sleep 0.5

python3 "$SERVE" --dir "$DOCROOT" --output "$DOCROOT/design-feedback.md" \
  --port "$BUSY" >"$TMP/busy.log" 2>&1 &
PIDS="$PIDS $!"
sleep 1.5

NEW_URL="$(grep -Eo 'http://127\.0\.0\.1:[0-9]+' "$TMP/busy.log" | tail -1 || true)"
NEW_PORT="${NEW_URL##*:}"
if [ -n "$NEW_URL" ] && [ "$NEW_PORT" != "$BUSY" ]; then
  ok "busy port $BUSY -> next free port $NEW_PORT ($NEW_URL)"
else
  bad "busy port $BUSY did not yield a new URL (got '${NEW_URL:-none}')"
fi
if grep -qi 'busy' "$TMP/busy.log"; then
  ok "server log surfaces busy-port message"
else
  bad "server log has no busy-port message"
fi
if [ -n "$NEW_URL" ] && wait_for "$NEW_URL/review" 30; then
  ok "fallback server answers on $NEW_URL"
else
  bad "fallback server unreachable"
fi

# --- Live review: POST red/green + text, assert design-feedback.md. ---
PORT="$(free_port)"
python3 "$SERVE" --dir "$DOCROOT" --output "$DOCROOT/design-feedback.md" \
  --port "$PORT" >"$TMP/server.log" 2>&1 &
PIDS="$PIDS $!"
BASE_URL="http://127.0.0.1:$PORT"

if wait_for "$BASE_URL/" 50; then
  ok "review server answers on $BASE_URL"
else
  bad "review server unreachable on $BASE_URL"
  echo "--- server.log ---"; cat "$TMP/server.log" 2>/dev/null || true
fi

PAGE="$TMP/review.html"
if curl -s --max-time 5 "$BASE_URL/" -o "$PAGE" 2>/dev/null; then
  if grep -qi 'red' "$PAGE" && grep -qi 'green' "$PAGE"; then
    ok "review page offers red/green verdicts"
  else
    bad "review page missing red/green verdicts"
  fi
  grep -q 'textarea' "$PAGE" \
    && ok "review page has text box" \
    || bad "review page missing text box"
  grep -q -i 'save' "$PAGE" \
    && ok "review page has Save hook" \
    || bad "review page missing Save hook"
else
  bad "could not fetch review page"
fi

# Script-parse guard (Task 4 blocker): served JS must be syntactically valid.
# Extracts <script>...</script> from $PAGE; node --check when available;
# always asserts literal backslash-n lines.join('\n') is shipped
# (old bug shipped a real newline -> SyntaxError, grep fails).
SCRIPT_JS="$TMP/review.js"
if python3 - "$PAGE" "$SCRIPT_JS" <<'PYEOF'
import sys
src = open(sys.argv[1], encoding="utf-8").read()
start = src.find("<script>")
end = src.find("</script>", start)
if start == -1 or end == -1:
    sys.exit("no <script> block found")
open(sys.argv[2], "w", encoding="utf-8").write(src[start + len("<script>"):end])
PYEOF
then
  if [ -s "$SCRIPT_JS" ]; then
    ok "review <script> extracted"
  else
    bad "review <script> extraction failed (empty)"
  fi
else
  bad "review <script> extraction failed"
fi
if command -v node >/dev/null 2>&1; then
  if node --check "$SCRIPT_JS" >"$TMP/nodecheck.log" 2>&1; then
    ok "review <script> passes node --check"
  else
    bad "review <script> fails node --check"
    cat "$TMP/nodecheck.log" 2>/dev/null || true
  fi
else
  ok "node unavailable, skipping node --check (grep guard still applies)"
fi
if grep -F -q "lines.join('\n')" "$PAGE"; then
  ok "review page ships literal lines.join backslash-n"
else
  bad "review page JS broken: literal lines.join backslash-n missing (newline leak?)"
fi

SECTION="hero-landing"
COMMENT="airy hero with one calm CTA keeps focus - sample comment 4f2a"
if curl -s --max-time 5 -X POST -H 'Content-Type: application/json' \
    -d "{\"section\":\"$SECTION\",\"verdict\":\"green\",\"comment\":\"$COMMENT\"}" \
    "$BASE_URL/save" -o "$TMP/save1.json" 2>/dev/null; then
  ok "POST green verdict + text accepted"
else
  bad "POST green verdict + text failed"
fi

SECTION2="pricing-grid"
COMMENT2="too dense, cards collide - sample comment 9b1c"
if curl -s --max-time 5 -X POST -H 'Content-Type: application/json' \
    -d "{\"section\":\"$SECTION2\",\"verdict\":\"red\",\"comment\":\"$COMMENT2\"}" \
    "$BASE_URL/save" -o "$TMP/save2.json" 2>/dev/null; then
  ok "POST red verdict + text accepted"
else
  bad "POST red verdict + text failed"
fi

MD="$DOCROOT/design-feedback.md"
if [ -f "$MD" ]; then
  ok "design-feedback.md written"
else
  bad "design-feedback.md missing"
fi

if [ -f "$MD" ]; then
  grep -qF "$SECTION" "$MD" \
    && ok "md contains section id '$SECTION'" \
    || bad "md missing section id '$SECTION'"
  grep -qF "green" "$MD" \
    && ok "md contains verdict 'green'" \
    || bad "md missing verdict 'green'"
  grep -qF "$COMMENT" "$MD" \
    && ok "md contains comment text" \
    || bad "md missing comment text"
  grep -qF "$SECTION2" "$MD" \
    && ok "md contains section id '$SECTION2'" \
    || bad "md missing section id '$SECTION2'"
  grep -qF "red" "$MD" \
    && ok "md contains verdict 'red'" \
    || bad "md missing verdict 'red'"
  grep -qF "$COMMENT2" "$MD" \
    && ok "md contains second comment text" \
    || bad "md missing second comment text"
fi

if curl -s --max-time 5 "$BASE_URL/download" -o "$TMP/export.md" 2>/dev/null \
    && grep -qF "$SECTION" "$TMP/export.md"; then
  ok "download export serves saved feedback"
else
  bad "download export missing or empty"
fi

# --- save_feedback.py CLI directly: patch-in-place, no duplicate headings. ---
cat > "$TMP/in.json" <<'EOF'
{"section": "cli-section", "verdict": "red", "comment": "cli comment 77aa"}
EOF
if python3 "$SAVE" --input "$TMP/in.json" --output "$TMP/cli-feedback.md" \
    >"$TMP/cli.log" 2>&1; then
  ok "save_feedback.py CLI exits 0"
else
  bad "save_feedback.py CLI exits non-zero"
fi
if grep -qF "cli-section" "$TMP/cli-feedback.md" 2>/dev/null \
    && grep -qF "red" "$TMP/cli-feedback.md" \
    && grep -qF "cli comment 77aa" "$TMP/cli-feedback.md"; then
  ok "save_feedback.py CLI persists section + verdict + comment"
else
  bad "save_feedback.py CLI output missing section/verdict/comment"
fi
# Re-save same section: heading patched, not duplicated.
cat > "$TMP/in2.json" <<'EOF'
{"section": "cli-section", "verdict": "green", "comment": "revised cli comment 88bb"}
EOF
python3 "$SAVE" --input "$TMP/in2.json" --output "$TMP/cli-feedback.md" \
  >/dev/null 2>&1
COUNT="$(grep -c '^## cli-section' "$TMP/cli-feedback.md" 2>/dev/null || echo 0)"
if [ "$COUNT" = "1" ] && grep -qF "revised cli comment 88bb" "$TMP/cli-feedback.md"; then
  ok "save_feedback.py patches existing section in place"
else
  bad "save_feedback.py duplicated section heading (count=$COUNT)"
fi

echo "---"
echo "passed=$PASS failed=$FAIL"
if [ "$FAIL" -eq 0 ]; then echo "RESULT: PASS"; else echo "RESULT: FAIL"; fi
[ "$FAIL" -eq 0 ]
