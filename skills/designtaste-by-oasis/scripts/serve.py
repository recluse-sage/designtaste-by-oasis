#!/usr/bin/env python3
"""Serve static wireframes + red/green review UI, persist to design-feedback.md.

Serves ``--dir`` (wireframe files for this run) on port 8000. If port 8000
is busy, the server tries the next free port and tells the user the URL -
it never crashes on a busy port. Use ``--port 0`` to let the OS pick.

Review UI (``/`` when no index.html exists, else ``/review``): one card per
design part with red/green verdict buttons revealed on hover, a text box,
and a per-card Save button plus Save-all. Saves POST JSON to ``/save`` and
are appended/patched into ``design-feedback.md`` at the run root via
save_feedback.py. ``/download`` exports the markdown file (the download
fallback if a save ever fails client-side the page also offers a
blob download so no answer is lost).

Stdlib only.

Usage:
    python3 serve.py [--dir WIREFRAMES] [--port 8000] [--output design-feedback.md]
"""

import argparse
import html
import json
import mimetypes
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DEFAULT_PORT = 8000
MAX_PORT_TRIES = 20
FEEDBACK_FILENAME = "design-feedback.md"

# Serializes concurrent /save writes from the threaded server so two
# verdict POSTs cannot interleave a read-modify-write on the markdown.
_SAVE_LOCK = threading.Lock()

FIXED_PARTS = [
    "sections",
    "buttons",
    "modals",
    "backgrounds",
    "color",
    "3D",
    "animation",
    "forms",
    "aesthetic",
    "arrangement",
]

REVIEW_CSS = """
:root { color-scheme: light dark; }
body { font-family: system-ui, -apple-system, sans-serif; max-width: 960px;
       margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }
header p { max-width: 65ch; }
.red { color: #b00020; } .green { color: #0a7a2f; }
.actions { display: flex; gap: 1rem; align-items: center; margin: 1rem 0; }
#save-all { padding: .4rem 1.2rem; cursor: pointer; }
.part { border: 1px solid #ccc; border-radius: 8px; padding: 1rem; margin: 1rem 0; }
.part:hover { border-color: #888; }
.part h2 { margin: 0 0 .25rem; font-size: 1.1rem; }
.part .hint { margin: 0 0 .5rem; font-size: .9rem; opacity: .75; }
.verdicts { opacity: 0; transition: opacity .15s; display: flex; gap: .5rem; }
.part:hover .verdicts, .part:focus-within .verdicts { opacity: 1; }
.v { cursor: pointer; border: 1px solid #999; background: none;
     padding: .3rem .9rem; border-radius: 999px; font-size: .9rem; }
.v.red.sel { background: #fde2e2; border-color: #b00020; }
.v.green.sel { background: #ddf5dd; border-color: #0a7a2f; }
textarea { width: 100%; min-height: 3rem; margin: .5rem 0; font: inherit; }
.save-one { cursor: pointer; }
"""

REVIEW_JS = r"""
async function postJSON(url, data) {
  var res = await fetch(url, {method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)});
  var text = await res.text();
  var body = null;
  try { body = JSON.parse(text); }
  catch (e) { throw {message: 'bad server response', payload: null}; }
  if (!res.ok || (body && body.ok === false)) {
    throw {message: (body && body.note) || ('save failed (' + res.status + ')'),
           payload: body};
  }
  return body;
}
function cardEntry(card) {
  var sel = card.querySelector('.v.sel');
  return {section: card.dataset.part,
          verdict: sel ? sel.dataset.v : '',
          comment: card.querySelector('textarea').value};
}
function setStatus(msg, isErr) {
  var el = document.getElementById('status');
  el.textContent = msg;
  el.style.color = isErr ? 'red' : 'green';
}
function mdFor(entries) {
  var lines = ['# Design Feedback', ''];
  entries.forEach(function (e) {
    lines.push('## ' + e.section, '',
      '- Verdict: ' + (e.verdict || 'undecided'),
      '- Comment: ' + (e.comment || ''), '');
  });
  return lines.join('\n');
}
function downloadFallback(entries, note) {
  var blob = new Blob([mdFor(entries)], {type: 'text/markdown'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'design-feedback.md';
  a.textContent = 'Download your feedback (save failed: ' + note + ')';
  var el = document.getElementById('status');
  el.innerHTML = '';
  el.appendChild(a);
}
async function saveEntries(entries) {
  if (!entries.length) {
    setStatus('Nothing to save yet - pick red/green or write a note.', true);
    return;
  }
  try {
    var body = await postJSON('/save', {feedbacks: entries});
    setStatus('Saved to ' + (body.output || 'design-feedback.md'));
  } catch (err) {
    setStatus('Save failed - use the download fallback so no answer is lost.', true);
    downloadFallback(entries, err.message);
  }
}
document.querySelectorAll('.part').forEach(function (card) {
  card.querySelectorAll('.v').forEach(function (btn) {
    btn.addEventListener('click', function () {
      card.querySelectorAll('.v').forEach(function (b) { b.classList.remove('sel'); });
      btn.classList.add('sel');
    });
  });
  card.querySelector('.save-one').addEventListener('click', function () {
    saveEntries([cardEntry(card)]);
  });
});
document.getElementById('save-all').addEventListener('click', function () {
  var entries = Array.prototype.map.call(
    document.querySelectorAll('.part'), cardEntry
  ).filter(function (e) { return e.verdict || e.comment; });
  saveEntries(entries);
});
"""

REVIEW_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wireframe review - designtaste-by-oasis</title>
<style>__CSS__</style>
</head>
<body>
<header>
<h1>Wireframe review</h1>
<p>Hover a part to reveal its <strong class="red">red</strong> /
<strong class="green">green</strong> verdict buttons, add a note in the
text box, then press Save. Feedback persists to
<code>design-feedback.md</code>. If saving fails the page offers a
download fallback so no answer is lost.</p>
<div class="actions"><button id="save-all" type="button">Save all</button>
<a id="dl" href="/download">Download design-feedback.md</a>
<span id="status" role="status"></span></div>
</header>
<main>
__CARDS__
</main>
<script>__JS__</script>
</body>
</html>
"""


def load_parts(docroot):
    """Part list for the review UI: ranked-parts.json wins, else fixed parts."""
    ranked = Path(docroot) / "ranked-parts.json"
    if ranked.is_file():
        try:
            data = json.loads(ranked.read_text(encoding="utf-8"))
            recs = data if isinstance(data, list) else data.get("parts", [])
            names = [r.get("part") for r in recs
                     if isinstance(r, dict) and r.get("part")]
            if names:
                examples = {r.get("part"): r for r in recs if isinstance(r, dict)}
                return [(n,
                         str(examples[n].get("example", "")),
                         str(examples[n].get("verdict", ""))) for n in names]
        except (json.JSONDecodeError, OSError, AttributeError):
            pass
    return [(part, "", "") for part in FIXED_PARTS]


def review_page(docroot):
    """Render the review HTML: red/green hover per part + text box + Save."""
    cards = []
    for part, example, verdict in load_parts(docroot):
        hint = example or verdict
        cards.append(
            '<section class="part" data-part="%s">\n'
            '  <h2>%s</h2>\n%s'
            '  <div class="verdicts" aria-label="verdict for %s">\n'
            '    <button type="button" class="v red" data-v="red">red &#10008;</button>\n'
            '    <button type="button" class="v green" data-v="green">green &#10004;</button>\n'
            '  </div>\n'
            '  <textarea aria-label="comment for %s" '
            'placeholder="What works / what should change..."></textarea>\n'
            '  <button type="button" class="save-one">Save</button>\n'
            '</section>'
            % (html.escape(part), html.escape(part),
               '  <p class="hint">%s</p>\n' % html.escape(hint) if hint else "",
               html.escape(part), html.escape(part))
        )
    return (REVIEW_TEMPLATE
            .replace("__CSS__", REVIEW_CSS)
            .replace("__JS__", REVIEW_JS)
            .replace("__CARDS__", "\n".join(cards)))


def coerce_post_entries(payload):
    """Accept one feedback object or {feedbacks: [...]} / form-encoded."""
    try:
        from save_feedback import normalize_entries
    except ImportError:
        normalize_entries = None
    if normalize_entries is not None:
        return normalize_entries(payload)
    # Minimal inline fallback if save_feedback.py is unavailable.
    items = payload.get("feedbacks", payload) if isinstance(payload, dict) else payload
    if isinstance(items, dict):
        items = [items]
    entries = []
    for item in items:
        section = " ".join(str(item.get("section", item.get("part", ""))).split())
        comment = " ".join(str(item.get("comment", "")).split())
        if section:
            entries.append({"section": section,
                            "verdict": str(item.get("verdict", "")).strip() or "undecided",
                            "comment": comment})
    if not entries:
        raise ValueError("no usable feedback entries")
    return entries


class ReviewHandler(BaseHTTPRequestHandler):
    docroot = Path(".")
    output_path = Path(FEEDBACK_FILENAME)
    server_version = "DesignTasteReview/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("review: " + fmt % args + "\n")

    def _send(self, code, body, ctype="text/html; charset=utf-8", extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path):
        ctype, _ = mimetypes.guess_type(str(path))
        try:
            data = path.read_bytes()
        except OSError as exc:
            return self._send(404, "not found: %s" % exc, "text/plain")
        return self._send(200, data, ctype or "application/octet-stream")

    def do_GET(self):  # noqa: N802 (http.server naming)
        path = urlparse(self.path).path
        if path in ("/review", "/review.html"):
            return self._send(200, review_page(self.docroot))
        if path in ("/", "/index.html"):
            index = Path(self.docroot) / "index.html"
            if index.is_file():
                # A run wireframe takes "/"; the review UI lives at /review.
                return self._serve_file(index)
            return self._send(200, review_page(self.docroot))
        if path in ("/download", "/export", "/api/download"):
            target = Path(self.output_path)
            if not target.is_file():
                return self._send(
                    404,
                    "no feedback saved yet - pick red/green verdicts and press Save first.",
                    "text/plain")
            return self._send(
                200, target.read_bytes(), "text/markdown; charset=utf-8",
                {"Content-Disposition":
                 'attachment; filename="%s"' % target.name})
        if path in ("/api/health", "/health"):
            return self._send(200, json.dumps({"ok": True}), "application/json")
        rel = path.lstrip("/")
        if not rel or ".." in rel.split("/"):
            return self._send(404, "not found", "text/plain")
        target = Path(self.docroot) / rel
        if target.is_dir():
            target = target / "index.html"
        if target.is_file():
            return self._serve_file(target)
        return self._send(404, "not found: %s" % html.escape(path), "text/plain")

    def _origin_allowed(self):
        """Minimal CSRF guard: a present Origin must match the served host."""
        origin = self.headers.get("Origin")
        if not origin:
            return True
        try:
            netloc = urlparse(origin).netloc
            hostname = urlparse(origin).hostname
        except Exception:
            return False
        host = self.headers.get("Host", "")
        if host:
            return netloc == host
        return hostname in ("127.0.0.1", "localhost")

    def do_POST(self):  # noqa: N802 (http.server naming)
        path = urlparse(self.path).path
        if path not in ("/save", "/api/save", "/feedback"):
            return self._send(404, "not found", "text/plain")
        if not self._origin_allowed():
            return self._send(403, json.dumps({"ok": False,
                                               "note": "origin not allowed"}),
                               "application/json")
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length > 0 else b""
        ctype = self.headers.get("Content-Type", "")
        try:
            if "application/json" in ctype or raw.lstrip()[:1] in (b"{", b"["):
                payload = json.loads(raw.decode("utf-8") or "{}")
            else:
                form = parse_qs(raw.decode("utf-8", "replace"))
                payload = {k: v[0] if len(v) == 1 else v
                           for k, v in form.items()}
            entries = coerce_post_entries(payload)
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            return self._send(400, json.dumps({"ok": False,
                                               "note": "bad feedback payload: %s" % exc}),
                              "application/json")
        try:
            from save_feedback import save_feedbacks
        except ImportError:
            save_feedbacks = None
        if save_feedbacks is None:
            return self._send(500, json.dumps({
                "ok": False,
                "note": "save_feedback.py unavailable; keep answers and use /download",
                "download_url": "/download"}), "application/json")
        try:
            with _SAVE_LOCK:
                result = save_feedbacks(entries, self.output_path)
        except ValueError as exc:
            return self._send(400, json.dumps({"ok": False, "note": str(exc)}),
                              "application/json")
        status = 200 if result["ok"] else 500
        body = {"ok": result["ok"], "note": result["note"],
                "output": result["path"],
                "saved": [e["section"] for e in entries]}
        if not result["ok"]:
            body["download_url"] = "/download"
            if result.get("fallback"):
                body["fallback"] = result["fallback"]
        return self._send(status, json.dumps(body), "application/json")


def bind_server(host, port):
    """Bind on port, else the next free port. Returns (server, actual, tried)."""
    if port == 0:
        server = ThreadingHTTPServer((host, 0), ReviewHandler)
        return server, server.server_address[1], []
    tried = []
    last_err = None
    for candidate in range(port, port + MAX_PORT_TRIES):
        try:
            return ThreadingHTTPServer((host, candidate), ReviewHandler), candidate, tried
        except OSError as exc:
            busy = (getattr(exc, "errno", None) in (13, 48, 98, 10013)
                    or "Address already in use" in str(exc))
            if not busy:
                raise
            tried.append(candidate)
            last_err = exc
    raise last_err


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dir", default=".",
                        help="wireframe files to serve (default: cwd)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help="preferred port (default: 8000; next free port on busy)")
    parser.add_argument("--host", default="127.0.0.1", help="bind host")
    parser.add_argument("--output", default=None,
                        help="feedback markdown path (default: <dir>/design-feedback.md)")
    args = parser.parse_args(argv)

    ReviewHandler.docroot = Path(args.dir)
    ReviewHandler.output_path = (Path(args.output) if args.output
                                 else ReviewHandler.docroot / FEEDBACK_FILENAME)

    try:
        server, actual, tried = bind_server(args.host, args.port)
    except OSError as exc:
        print("ERROR: no free port near %d (%s)" % (args.port, exc), file=sys.stderr)
        return 1
    server.daemon_threads = True
    for busy in tried:
        print("Port %d busy, trying next free port..." % busy, flush=True)
    url = "http://%s:%d" % (args.host, actual)
    print("Serving wireframes from %s at %s" % (ReviewHandler.docroot.resolve(), url),
          flush=True)
    if tried:
        print("Port %d busy, using next free port %d: %s" % (tried[0], actual, url),
              flush=True)
    print("Review UI: %s/review" % url, flush=True)
    print("Feedback file: %s" % Path(ReviewHandler.output_path).resolve(), flush=True)
    print("Download fallback: %s/download" % url, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
