# designtaste-by-oasis

Thin orchestrator skill that runs website visual direction end-to-end:
mandatory brainstorming first, then layout, taste, buttons, copy-slim,
3 wireframes, clickable review on `:8000`, and a detailed
`design-system.md`.

Solo dev, local files. No hosted backend in v1.

## Layout

- `skills/designtaste-by-oasis/SKILL.md` - thin router (TOC + ordered
  Invoke steps, body <500 lines).
- `skills/designtaste-by-oasis/references/` - phase detail, one level
  deep from SKILL.md, no chains.
- `skills/designtaste-by-oasis/scripts/` - deterministic helpers (port
  server, save, validators).
- `skills/designtaste-by-oasis/assets/` - curated defaults.
- `tests/` - deterministic graders (`test_*.sh`).
- `spec.md` - design doc. `implementation-plan.md` - build plan.

## Install

For Claude Code, this repo ships as a plugin bundle (`.claude-plugin/plugin.json` +
this README). For skills.sh / OpenCode, each skill is one folder with
its own `SKILL.md`.

## Install & findability

Keywords: visual direction, wireframe review, design system, website taste.

- Claude Code: install this repo as a plugin bundle (uses `.claude-plugin/plugin.json`
  + this README), or copy `skills/designtaste-by-oasis` into your
  skills folder.
- skills.sh: this skill targets listing under `designtaste-by-oasis`
  (will be listed once install telemetry confirms it). Verify any
  install with the `tool_used:Skill` grader after each
  description change.
- OpenCode / generic CLI: `npx skills add oasis/designtaste-by-oasis`
- Pinned install: `gh skill install oasis/designtaste-by-oasis designtaste-by-oasis --pin <SHA>`
- Local check: `skills-ref validate ./skills/designtaste-by-oasis`
