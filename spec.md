# designtaste-by-oasis - Design Doc
Date: 2026-10-21
Status: Draft for review
Name: designtaste-by-oasis (unique; design-taste and design-taste-frontend taken)

## 1. Goal
Thin orchestrator skill that runs website visual-direction end-to-end: brainstorming mandatory first, then layout, taste, buttons, copy-slim, 3 wireframes, clickable review, detailed design-system.md.

Solo dev, local files. No hosted backend in v1.

## 2. Architecture (thin orchestrator)
- Folder `designtaste-by-oasis/` with `SKILL.md` (<500 lines, <5000 tokens) as TOC + ordered Invoke steps.
- `references/` for phase detail (one level deep, no chains). `scripts/` for deterministic helpers (port server, save, validators). `assets/` for curated defaults.
- Other skills stay separate folders in same repo for GitHub/skills.sh/OpenCode. For Claude Code ship as plugin bundle (.claude-plugin/plugin.json + README).
- Router does no heavy work. It detects stage, invokes sub-skill via skill tool by name, validates return.
- Gate wording: `Only proceed when requirements met`, `NEVER proceed without explicit user approval`. Hard block only via Stop hooks where available.

Flow:
check arch file → brainstorming (mandatory Step 1) → questionnaire → collect/rank → 3 static wireframes → :8000 review → design-feedback.md → refine → pick one → design-system.md

## 3. Components
- Router: checklist, phase gates, missing-skill fallback.
- V1 invoked:
  - brainstorming (mandatory)
  - aesthetic/layout + IA/wireframe/hierarchy/tokens
  - design-taste direction (thin profile)
  - buttons core + states (default/hover/active/disabled/loading/error/empty)
  - copy-slim (scannability, CTA placement, draft copy allowed)
  - review server (static HTML/CSS on :8000, red/green hover per part, text box, Save)
  - system writer (detailed design-system.md + check-ask-update rule)
- Later:
  - icons full system (library, sizing, a11y)
  - animation full choreography (timelines, scroll, physics). V1 keeps only opportunity-scan + reduced-motion + perf guards.
- Questionnaire: 5 quick Q + 2-3 liked links + 1 disliked with why.
- Examples: systemdesignhunt + user URLs. No crawler in v1. Fixed breakdown checklist: sections, buttons, modals, backgrounds, color, 3D, animation, forms, aesthetic, arrangement.

## 4. Data flow
1. Arch file in → questionnaire answers out. If missing, ask, don't assume.
2. Answers + links in → ranked parts list out.
3. Ranked list in → 3 static HTML/CSS wireframes out.
4. Wireframes + clicks/text on :8000 in → design-feedback.md out (+ download .md export), then refined wireframes.
5. Picked direction in → design-system.md out.
Files: repo root `design-feedback.md`, `design-system.md`. Review page reads first, writes second.

## 5. Error handling
- Missing arch → stop and ask.
- Brainstorming skipped → block, re-invoke Step 1.
- No examples / source unreachable → curated defaults + warn.
- Port 8000 busy → try next free port once, tell user URL.
- Save fails → keep in memory + offer download fallback.
- Sub-skill missing → minimal inline rules + suggest install via find-skills.
- Future deviation → check design-system.md first, ask if deviating, update on approval.

## 6. Testing
- Trigger: 10 should-load + 10 should-not prompts.
- Gate: skip-brainstorming attempt must block.
- Phase: one sample brief through layout/taste/buttons/copy-slim, check outputs exist and short.
- Review: red/green + text saves to md + export works.
- Handoff: design-system.md has tokens not values, states, breakpoints, animation.
- Regression: validate --strict + rerun evals; compare with/without skill (delta proves value). Prefer deterministic graders (file_exists, tool_used, regex).

## 7. Distribution / findability
- Public repo, one folder per skill with SKILL.md. README + .claude-plugin/plugin.json (description, author, homepage, repository) for Claude Code.
- Description: third-person, 1-1024 chars, front-load use case + keywords: visual direction, wireframe review, design system, website taste.
- List on skills.sh. Verify with `skills-ref validate`, local install, `tool_used:Skill` grader after each description change.

## 8. Open questions (v1 scope lock)
- Confirm curated defaults list (6-8) to ship in assets/.
- Confirm questionnaire 5 questions wording.
- Confirm server language (node vs python) for :8000 saver.
