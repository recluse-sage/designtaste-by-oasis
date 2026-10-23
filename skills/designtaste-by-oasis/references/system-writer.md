# System writer

You turn the picked wireframe plus `design-feedback.md` into the
detailed `design-system.md` at the run root. Copy
`DESIGN-SYSTEM-TEMPLATE.md` from the repo root and fill every section;
never invent a parallel structure.
Shipped copy: `assets/DESIGN-SYSTEM-TEMPLATE.md` (same content as the repo root, packaged for `npx skills add`).

## Inputs (all required before writing)

- The picked direction: which of the 3 wireframes the user chose, said
  explicitly by the user. If no pick exists, stop and ask. Never assume.
- `design-feedback.md` at the run root: per-section verdicts
  (red/green) plus comments. Green parts are kept, red parts are
  reworked - record the outcome per part in the feedback summary.
- The ranked parts list and the picked wireframe itself, for reference.

## Rules

- Tokens, not values: write token names (e.g.
  `--color-surface-primary`) plus usage rules. Never hard-code raw
  values as the source of truth - no hex, px, or font names standing
  alone. Values live in code; names live here.
- Every button variant (primary, secondary, text/ghost) ships all seven
  states: default, hover, active, disabled, loading, error, empty.
  A missing state is a defect.
- Layout, breakpoints, and animation notes are mandatory sections even
  when the answer is "keep it minimal" - say what and why.
- V1 animation scope only: opportunity-scan, reduced-motion support,
  and performance guards. Full choreography is deferred.
- Always include the check-ask-update rule block verbatim from the
  template. Do not paraphrase it away.

## Steps

1. Copy the template to `design-system.md` at the run root.
2. Fill the direction summary: picked direction id plus a one-line
   feedback basis per decided part (kept / reworked).
3. Fill tokens, components, layout, breakpoints, and animation from
   the picked wireframe, constrained by the green verdicts.
4. Re-check: every template section filled, no raw values, all states
   present, no `{{placeholder}}` left, rule block untouched.
5. Tell the user where `design-system.md` was written and what was
   decided.

## Output

A complete `design-system.md` at the run root with all template
sections filled, plus the check-ask-update rule for future deviations.
