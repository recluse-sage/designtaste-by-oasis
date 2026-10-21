#!/usr/bin/env python3
"""Persist red/green verdicts + comments to design-feedback.md.

Reads feedback JSON (one object, or {"feedbacks": [...]} / a list of
objects) shaped like::

    {"section": "hero-landing", "verdict": "green", "comment": "..."}

``section`` also accepts the aliases ``section_id`` / ``part`` / ``id``;
``comment`` accepts ``text`` / ``note``. Each entry is stored under a
``## <section>`` heading in the output markdown; re-saving a section
patches its block in place instead of duplicating it, so other sections
are preserved.

Write failures never lose answers: the rendered markdown is printed
between DOWNLOAD markers for copy/paste, a ``*.download.md`` fallback
file is attempted, and the result dict / exit code reports which path
was taken (exit 0 = primary file written, exit 2 = fallback only).

Stdlib only. Importable: ``from save_feedback import save_feedbacks``.

Usage:
    python3 save_feedback.py --input feedback.json --output design-feedback.md
    python3 save_feedback.py --section hero --verdict green --comment "nice"
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

FEEDBACK_FILENAME = "design-feedback.md"

HEADER_TITLE = "# Design Feedback"
HEADER_NOTE = (
    "_Red/green verdicts + comments collected on the :8000 review page._"
)


def normalize_entries(data):
    """Normalize feedback JSON into [{section, verdict, comment}]."""
    if isinstance(data, dict):
        for key in ("feedbacks", "items", "reviews", "entries"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
        else:
            data = [data]
    if not isinstance(data, list):
        raise ValueError("feedback JSON must be an object or an array of objects")
    entries = []
    for item in data:
        if not isinstance(item, dict):
            continue
        section = str(
            item.get("section",
                     item.get("section_id",
                              item.get("part", item.get("id", "")))) or ""
        ).strip()
        verdict = str(
            item.get("verdict",
                     item.get("vote", item.get("color", ""))) or ""
        ).strip().lower()
        comment = str(
            item.get("comment",
                     item.get("text", item.get("note", ""))) or ""
        )
        # Flatten newlines so a "## " line inside a comment/section cannot
        # create a phantom section heading on the next in-place patch.
        section = " ".join(section.split())
        comment = " ".join(comment.split())
        if not section:
            continue
        entries.append({
            "section": section,
            "verdict": verdict or "undecided",
            "comment": comment.strip(),
        })
    if not entries:
        raise ValueError("no usable feedback entries (need section + verdict)")
    return entries


def split_sections(text):
    """Split markdown into (preamble_lines, {section: lines}, [order])."""
    preamble = []
    sections = {}
    order = []
    current = None
    for line in text.splitlines():
        match = re.match(r"##\s+(.*?)\s*$", line)
        if match:
            current = match.group(1).strip()
            if current not in sections:
                sections[current] = []
                order.append(current)
            sections[current].append(line)
        elif current is None:
            preamble.append(line)
        else:
            sections[current].append(line)
    return preamble, sections, order


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def render_markdown(existing_text, entries, stamp=None):
    """Merge entries into markdown text (patch existing sections)."""
    stamp = stamp or utc_stamp()
    if existing_text and existing_text.strip():
        preamble, sections, order = split_sections(existing_text)
        while preamble and not preamble[-1].strip():
            preamble.pop()
    else:
        preamble, sections, order = [HEADER_TITLE, "", HEADER_NOTE, ""], {}, []
    if not preamble or preamble[0].strip() != HEADER_TITLE:
        preamble = [HEADER_TITLE, ""] + [ln for ln in preamble if ln.strip() != HEADER_TITLE]
    for entry in entries:
        section = " ".join(str(entry.get("section", "")).split())
        verdict = str(entry.get("verdict", "undecided"))
        comment = " ".join(str(entry.get("comment", "")).split())
        block = [
            "## %s" % section,
            "",
            "- Verdict: %s" % verdict,
            "- Comment: %s" % comment,
            "- Updated: %s" % stamp,
            "",
        ]
        if section not in sections:
            order.append(section)
        sections[section] = block
    parts = preamble + [""]
    for name in order:
        parts.extend(sections[name])
    return "\n".join(parts).rstrip() + "\n"


def fallback_candidates(output):
    """Where to try the download fallback (sibling, then run root)."""
    sibling = output.with_name(output.stem + ".download" + output.suffix)
    return [sibling, Path.cwd() / "design-feedback.download.md"]


def save_feedbacks(entries, output_path):
    """Persist entries; on write error fall back without losing answers.

    Returns {"ok", "note", "markdown", "path", "fallback"}.
    """
    output = Path(output_path)
    try:
        existing = output.read_text(encoding="utf-8") if output.exists() else ""
    except OSError:
        existing = ""
    markdown = render_markdown(existing, entries)
    try:
        if str(output.parent) not in ("", ".") :
            output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
        return {
            "ok": True,
            "note": "saved %d feedback entr%s to %s"
                    % (len(entries), "y" if len(entries) == 1 else "ies", output),
            "markdown": markdown,
            "path": str(output),
            "fallback": None,
        }
    except OSError as exc:
        written = None
        for candidate in fallback_candidates(output):
            try:
                if str(candidate.parent) not in ("", "."):
                    candidate.parent.mkdir(parents=True, exist_ok=True)
                candidate.write_text(markdown, encoding="utf-8")
                written = str(candidate)
                break
            except OSError:
                continue
        note = ("primary write to %s failed (%s); answers preserved via "
                "download fallback%s"
                % (output, exc,
                   " at %s" % written if written else " (see output below)"))
        return {
            "ok": False,
            "note": note,
            "markdown": markdown,
            "path": str(output),
            "fallback": written,
        }


def load_input_file(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise ValueError("input file %s not found" % path)
    except json.JSONDecodeError as exc:
        raise ValueError("input file %s is not valid JSON (%s)" % (path, exc))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", default=None,
                        help="feedback JSON file (object or array)")
    parser.add_argument("--output", default=FEEDBACK_FILENAME,
                        help="markdown file to write (default: design-feedback.md)")
    parser.add_argument("--section", default=None, help="single-entry section id")
    parser.add_argument("--verdict", default="",
                        help="single-entry verdict: red or green")
    parser.add_argument("--comment", default="", help="single-entry comment")
    args = parser.parse_args(argv)

    try:
        if args.input:
            entries = normalize_entries(load_input_file(args.input))
        elif args.section:
            entries = normalize_entries({
                "section": args.section,
                "verdict": args.verdict,
                "comment": args.comment,
            })
        else:
            parser.error("need --input FILE or --section ID (with --verdict/--comment)")
    except ValueError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1

    try:
        result = save_feedbacks(entries, args.output)
    except ValueError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1

    if result["ok"]:
        print(result["note"])
        return 0

    print("PRIMARY SAVE FAILED: %s" % result["note"], file=sys.stderr)
    print("--- DOWNLOAD FALLBACK: copy below into %s ---" % result["path"])
    print(result["markdown"], end="")
    print("--- END DOWNLOAD FALLBACK ---")
    return 2


if __name__ == "__main__":
    sys.exit(main())
