# designtaste-by-oasis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build thin orchestrator skill designtaste-by-oasis with V1 phases and local review.

**Architecture:** Thin router SKILL.md with ordered Invoke steps and gates; phase detail in references/; deterministic helpers in scripts/; no nested refs.

**Tech Stack:** SKILL.md markdown, static HTML/CSS wireframes, node or python micro-server for :8000 save, markdown files for feedback/system.

**Spec:** `/Users/selim/Desktop/Personal/designtaste-by-oasis/spec.md`

## Global Constraints
- SKILL.md body <500 lines / <5000 tokens.
- References one level deep from SKILL.md, no chains.
- Name regex `^[a-z0-9]+(-[a-z0-9]+)*$`; folder matches name.
- Description third-person, 1-1024 chars, front-load use case + keywords.
- Brainstorming is mandatory Step 1; NEVER proceed without explicit approval.
- V1 only: layout, taste-direction, buttons core, copy-slim, review server, system writer. Icons full + animation full deferred.
- Solo dev, local files; no hosted backend in v1.

## Review Focus
- Skipped brainstorming still blocks with clear message, expected block not silent pass.
- Missing arch file asks instead of hallucinating, expected question not fabricated structure.
- Port 8000 busy surfaces new URL, expected usable link not crash.
- Save failure preserves answers via download fallback, expected no data loss.
- Sub-skill missing falls back to minimal inline rules + install hint, expected degraded but usable run.

---

### Task 1: Scaffold + router SKILL.md

**Files:**
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/SKILL.md`
- Create: `designtaste-by-oasis/README.md`
- Create: `designtaste-by-oasis/.claude-plugin/plugin.json`
- Test: `designtaste-by-oasis/tests/test_scaffold.sh`

**Interfaces:**
- Consumes: spec.md Sections 2-3
- Produces: skill name `designtaste-by-oasis`, Invoke order list used by Tasks 2-5

- [ ] **Step 1: Write failing test** - `test_scaffold.sh` asserts SKILL.md exists, name matches folder, description non-empty, body <500 lines.
- [ ] **Step 2: Run test to verify it fails** - Run: `bash designtaste-by-oasis/tests/test_scaffold.sh` Expected: FAIL missing file.
- [ ] **Step 3: Implement SKILL.md, README.md, .claude-plugin/plugin.json** - TOC + ordered Invoke steps + gate wording `Only proceed when requirements met`.
- [ ] **Step 4: Run test to verify it passes** - Run: `bash designtaste-by-oasis/tests/test_scaffold.sh` Expected: PASS.
- [ ] **Step 5: Validate** - Run: `skills-ref validate ./designtaste-by-oasis/skills/designtaste-by-oasis` if available; or `wc -l` check. Expected: valid / <500 lines.

### Task 2: References (phases + gates)

**Files:**
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/references/brainstorm-gate.md`
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/references/layout.md`
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/references/taste.md`
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/references/buttons.md`
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/references/copy-slim.md`
- Test: `designtaste-by-oasis/tests/test_refs.sh`

**Interfaces:**
- Consumes: Task 1 Invoke order
- Produces: phase file paths linked directly from SKILL.md (no nesting)

- [ ] **Step 1: Write failing test** - asserts all 5 refs exist and SKILL.md links each with one-level relative path.
- [ ] **Step 2: Run test to verify it fails** - Run: `bash designtaste-by-oasis/tests/test_refs.sh` Expected: FAIL.
- [ ] **Step 3: Implement 5 reference files** - gate checklist in brainstorm-gate.md; fixed part checklist (sections, buttons, modals, backgrounds, color, 3D, animation, forms, aesthetic, arrangement) in layout/taste; states list in buttons.md; scannability + CTA rules in copy-slim.md.
- [ ] **Step 4: Run test to verify it passes** - Run: `bash designtaste-by-oasis/tests/test_refs.sh` Expected: PASS.

### Task 3: Questionnaire + collector + wireframe builder

**Files:**
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/references/questionnaire.md`
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/scripts/collect.py`
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/assets/curated-defaults.md`
- Test: `designtaste-by-oasis/tests/test_collect.sh`

**Interfaces:**
- Consumes: Task 2 layout/taste refs
- Produces: `ranked-parts.json` shape `{part, example, verdict}` used by Task 4

- [ ] **Step 1: Write failing test** - with sample answers + 2 links, `collect.py` outputs ranked-parts.json with all fixed parts covered.
- [ ] **Step 2: Run test to verify it fails** - Run: `bash designtaste-by-oasis/tests/test_collect.sh` Expected: FAIL missing script.
- [ ] **Step 3: Implement questionnaire.md (5Q + 2-3 liked +1 disliked why), collect.py (systemdesignhunt + user URLs, fallback to curated-defaults on fetch fail), 6-8 defaults file.**
- [ ] **Step 4: Run test to verify it passes** - Run: `bash designtaste-by-oasis/tests/test_collect.sh` Expected: PASS + ranked-parts.json valid JSON.

### Task 4: Review server + feedback persistence

**Files:**
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/scripts/serve.py`
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/scripts/save_feedback.py`
- Test: `designtaste-by-oasis/tests/test_review.sh`

**Interfaces:**
- Consumes: Task 3 ranked-parts + 3 static wireframes (generated per-run, not shipped)
- Produces: `design-feedback.md` at run root + download export

- [ ] **Step 1: Write failing test** - start server, POST sample red/green + text for one section, assert design-feedback.md contains section id + verdict + comment.
- [ ] **Step 2: Run test to verify it fails** - Run: `bash designtaste-by-oasis/tests/test_review.sh` Expected: FAIL no server.
- [ ] **Step 3: Implement serve.py (static serve on 8000, next free port on busy, hover red/green UI hook) + save_feedback.py (append/patch md, download fallback on write error).**
- [ ] **Step 4: Run test to verify it passes** - Run: `bash designtaste-by-oasis/tests/test_review.sh` Expected: PASS + md updated.

### Task 5: System writer + consistency rule + distribution

**Files:**
- Create: `designtaste-by-oasis/skills/designtaste-by-oasis/references/system-writer.md`
- Create: `designtaste-by-oasis/DESIGN-SYSTEM-TEMPLATE.md`
- Modify: `designtaste-by-oasis/README.md`
- Test: `designtaste-by-oasis/tests/test_system.sh`

**Interfaces:**
- Consumes: Tasks 1-4 outputs
- Produces: shippable repo (README + .claude-plugin/plugin.json + validate clean)

- [ ] **Step 1: Write failing test** - from sample feedback, template renders design-system.md with tokens not values, all states, layout, breakpoints, animation notes, plus check-ask-update rule text.
- [ ] **Step 2: Run test to verify it fails** - Run: `bash designtaste-by-oasis/tests/test_system.sh` Expected: FAIL.
- [ ] **Step 3: Implement system-writer.md + template + README install/findability section (keywords, skills.sh, npx skills add).**
- [ ] **Step 4: Run test + full suite** - Run: `bash designtaste-by-oasis/tests/test_*.sh` + `skills-ref validate` if present. Expected: all PASS.
