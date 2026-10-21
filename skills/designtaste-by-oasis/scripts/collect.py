#!/usr/bin/env python3
"""Collect taste examples and rank the fixed design parts.

Input: answers JSON with questionnaire answers plus example links, e.g.
    {
      "answers": {"q1": "airy, sharp, calm", "q2": "founders; book a demo", ...},
      "liked": ["https://example.com/a", "https://example.com/b"],
      "disliked": {"url": "https://example.com/c", "why": "too busy"}
    }
Also accepts "liked_links"/"links" for liked, and a plain string for
disliked. An optional "sources" list adds extra URLs (e.g. systemdesignhunt
picks) to try before falling back.

Output: ranked-parts.json - a JSON array with one record per fixed part:
    [{"part": "sections", "example": "...", "verdict": "..."}, ...]

Sources: systemdesignhunt picks + user URLs. Any URL that cannot be
fetched (short timeout) falls back to assets/curated-defaults.md, with a
warning on stderr. The output always covers all ten fixed parts.
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

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

BASE_VERDICTS = {
    "sections": "stacked single-focus sections, hero first, one CTA per section",
    "buttons": "one primary pill CTA per section; quiet secondary links",
    "modals": "overlays only for forms or media; explicit close, no surprises",
    "backgrounds": "flat light rhythm with one dark contrast band",
    "color": "neutral surfaces, single accent reserved for CTAs",
    "3D": "flat-first; depth only where it aids hierarchy",
    "animation": "minimal entrance and hover motion only; reduced-motion safe",
    "forms": "short inline forms, few fields, submit close to inputs",
    "aesthetic": "airy, sharp, calm; generous whitespace, no clutter",
    "arrangement": "single-column flow widening to a simple grid on large screens",
}

FETCH_TIMEOUT = 5


def try_fetch(url):
    """Return True if the URL responds, False on any failure."""
    if urlparse(url).scheme not in ("http", "https"):
        return False
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "designtaste-collect/1.0"}
        )
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            resp.read(1024)
            return 200 <= resp.status < 400
    except Exception:
        return False


def load_defaults(path):
    """Parse curated-defaults.md into [{title, url}] in file order."""
    entries = []
    title = None
    url = None
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"WARN: cannot read defaults file {path}: {exc}", file=sys.stderr)
        return entries
    for line in text.splitlines():
        m = re.match(r"##\s+\d+\.\s+(.*)", line.strip())
        if m:
            if title is not None:
                entries.append({"title": title, "url": url or ""})
            title = m.group(1).strip()
            url = None
        elif title is not None and url is None:
            u = re.search(r"https?://[^\s)>,]+", line)
            if u:
                url = u.group(0).rstrip(".,;")
    if title is not None:
        entries.append({"title": title, "url": url or ""})
    return entries


def load_answers(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"WARN: {path} is not a JSON object; ignoring", file=sys.stderr)
            return {}
        return data
    except FileNotFoundError:
        print(f"WARN: answers file {path} missing; using defaults", file=sys.stderr)
        return {}
    except json.JSONDecodeError as exc:
        print(f"WARN: answers file {path} invalid JSON ({exc}); using defaults",
              file=sys.stderr)
        return {}


def split_links(data):
    liked = data.get("liked", data.get("liked_links", data.get("links", [])))
    if isinstance(liked, str):
        liked = [liked]
    liked = [u for u in liked if isinstance(u, str) and u.strip()]
    sources = data.get("sources", [])
    if isinstance(sources, str):
        sources = [sources]
    sources = [u for u in sources if isinstance(u, str) and u.strip()]
    disliked = data.get("disliked", data.get("disliked_link", ""))
    disliked_url = ""
    disliked_why = ""
    if isinstance(disliked, dict):
        disliked_url = str(disliked.get("url", "") or "")
        disliked_why = str(disliked.get("why", "") or "")
    elif isinstance(disliked, str):
        disliked_url = disliked
    return liked, sources, disliked_url.strip(), disliked_why.strip()


def host_of(url):
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="answers.json",
                        help="answers + links JSON file")
    parser.add_argument("--output", default="ranked-parts.json",
                        help="where to write ranked parts JSON")
    parser.add_argument("--defaults", default=str(here / ".." / "assets"
                                                  / "curated-defaults.md"),
                        help="curated defaults fallback file")
    args = parser.parse_args()

    data = load_answers(args.input)
    answers = data.get("answers", {}) if isinstance(data.get("answers"), dict) else {}
    liked, sources, disliked_url, disliked_why = split_links(data)

    candidates = list(dict.fromkeys(liked + sources))
    reachable = [u for u in candidates if try_fetch(u)]
    failed = [u for u in candidates if u not in reachable]

    defaults = load_defaults(args.defaults)
    fallback_entry = defaults[0] if defaults else {"title": "curated defaults",
                                                   "url": ""}

    if failed:
        print(f"WARN: {len(failed)} of {len(candidates)} example URL(s) "
              f"unreachable; falling back to curated-defaults.md", file=sys.stderr)
        for u in failed:
            print(f"WARN: unreachable: {u}", file=sys.stderr)

    if reachable:
        example = reachable[0]
        example_note = f"{example} (user example)"
    else:
        if not candidates:
            print("WARN: no example URLs given; using curated-defaults.md",
                  file=sys.stderr)
        example = (f"{fallback_entry['title']} {fallback_entry['url']}".strip()
                   + " (curated-defaults fallback)")
        example_note = example

    taste_words = str(answers.get("q1", "") or "").strip()
    primary_action = str(answers.get("q2", "") or "").strip()

    records = []
    for part in FIXED_PARTS:
        verdict = BASE_VERDICTS[part]
        if part == "aesthetic" and taste_words:
            verdict += f"; user words: {taste_words}"
        if part == "aesthetic" and disliked_why:
            verdict += f"; avoid: {disliked_why}"
        if part == "buttons" and primary_action:
            verdict += f"; primary action: {primary_action}"
        if disliked_url and part in ("aesthetic", "arrangement"):
            verdict += f" (not this: {host_of(disliked_url) or disliked_url})"
        records.append({"part": part, "example": example_note, "verdict": verdict})

    out = Path(args.output)
    out.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} ranked parts to {out} "
          f"({'fallback' if not reachable else 'examples ok'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
