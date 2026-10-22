---
name: designtaste-by-oasis
description: Helps with website visual direction, wireframe review, and design system notes. It starts with brainstorming, then covers layout, website taste, buttons, and short copy to make three wireframes to click through and a clear design-system.md. Use it when the user wants help with visual direction, wireframe review, design system output, or website taste choices.
license: MIT
metadata:
  version: 0.1.0
---

# designtaste-by-oasis

Thin orchestrator for website visual direction end-to-end.

Scope: this skill operates on the run root by default (the directory where it is invoked); `--output` / `--dir` accept explicit paths. Run artifacts (design-feedback.md, design-system.md) are written there.

## Contents

- [Invoke order](#invoke-order)
- [Brainstorming (mandatory gate)](references/brainstorm-gate.md)
- [Layout](references/layout.md)
- [Taste direction](references/taste.md)
- [Buttons](references/buttons.md)
- [Copy slim](references/copy-slim.md)
- [Questionnaire](references/questionnaire.md)
- [System writer](references/system-writer.md)

## Invoke order

Follow these steps in order. This skill is a thin router: it detects
the stage, invokes the relevant phase, and validates the return. It
does no heavy design work itself.

### Step 1 - Brainstorming (mandatory, gated)

Brainstorming is mandatory and always runs first. NEVER proceed without
explicit user approval. Only proceed when requirements met: a written
brief with goal, audience, and scope, plus explicit user approval of
that brief.

- Read [references/brainstorm-gate.md](references/brainstorm-gate.md).
- If the user tries to skip brainstorming, block and re-invoke this
  step with a clear message. An expected block is not a silent pass.
- If the architecture input file is missing, stop and ask for it.
  Do not hallucinate structure; ask instead.

### Step 2 - Layout

- Read [references/layout.md](references/layout.md).
- Capture IA, section hierarchy, and wireframe skeleton before any
  visual styling.

### Step 3 - Taste direction

- Read [references/taste.md](references/taste.md).
- Build a thin taste profile from examples (systemdesignhunt plus
  user URLs) before committing to tokens.

### Step 4 - Buttons

- Read [references/buttons.md](references/buttons.md).
- Define the core button set with all states: default, hover, active,
  disabled, loading, error, empty.

### Step 5 - Copy slim

- Read [references/copy-slim.md](references/copy-slim.md).
- Draft short, scannable copy with clear CTA placement. Draft copy is
  allowed at this stage.

### Step 6 - Questionnaire and collect

- Read [references/questionnaire.md](references/questionnaire.md).
- Ask the 5 quick questions plus 2-3 liked links and 1 disliked link
  with why, then record verdicts for each fixed part into `ranked-parts.json`.

### Step 7 - Three wireframes

- Generate 3 static HTML/CSS wireframe directions from the ranked
  parts list. Wireframes are per-run artifacts, not shipped files.

### Step 8 - Review on :8000

- Serve the wireframes on port 8000 (local static server; if port
  8000 is busy, use the next free port and tell the user the URL).
- The review page supports red/green hover verdicts per part plus a
  text box and Save.

### Step 9 - design-feedback.md

- Persist review verdicts and comments to `design-feedback.md` at the
  run root. If saving fails, keep answers in memory and offer a
  download fallback so no data is lost.

### Step 10 - Refine

- Apply the feedback to the wireframes and re-review until the user
  picks one direction.

### Step 11 - design-system.md

- Read [references/system-writer.md](references/system-writer.md).
- Write the detailed `design-system.md` (tokens not values, all
  states, layout, breakpoints, animation notes) for the picked
  direction, plus the check-ask-update rule for future deviations.
