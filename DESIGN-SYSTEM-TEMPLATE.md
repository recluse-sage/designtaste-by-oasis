<!-- A calm place to keep what you picked and why. -->
<!-- Copy this file, then fill in each part below. -->

# design-system.md - {{PROJECT_NAME}}

> Generated {{DATE}} from picked direction **{{PICKED_DIRECTION}}**.
> Feedback basis: {{FEEDBACK_SUMMARY}}.
> Source: `design-feedback.md` at the run root plus the picked wireframe.

## 1. Direction summary

- Picked direction: {{PICKED_DIRECTION}}.
- Feedback basis: {{FEEDBACK_SUMMARY}}.
- Green-verdict parts are kept as specified below; red-verdict parts
  were reworked as noted. Any part not mentioned here is unchanged
  from the picked wireframe.

## 2. Design tokens (tokens, not values)

Token names are the source of truth. Raw values (hex, px, font files)
live in code, never here. Reference tokens by name everywhere below.

- `--color-surface-primary` - main page background token.
- `--color-surface-raised` - cards, modals, raised panels.
- `--color-text-primary` - headings and body copy.
- `--color-text-muted` - secondary copy, captions.
- `--color-action-primary` - primary button and link accent.
- `--color-action-on-primary` - text/icons on the primary action.
- `--color-border-subtle` - hairlines and dividers.
- `--color-state-error` - error text, borders, and icons.
- `--font-display` - headings token (stack defined in code).
- `--font-body` - body copy token.
- `--space-section` - vertical rhythm between sections.
- `--space-block` - spacing inside a section.
- `--radius-control` - buttons, inputs, small surfaces.
- `--radius-card` - cards, modals, large surfaces.
- `--shadow-raised` - raised surfaces and open modals.

Usage rules: one primary action color per view; error color only for
errors, never decoration; muted text never for primary copy.

## 3. Typography (token references)

- Display: `--font-display`, headings carry meaning alone (copy-slim:
  under ~8 words, one idea per block).
- Body: `--font-body`, short lines, bullets over paragraphs for 3+
  items.
- CTA labels: verb-first, 1-3 words, marked primary / secondary.

## 4. Buttons - all states (3 variants x 7 states)

Every variant below ships every state. A missing state is a defect.

### Primary (single main action per view)

- default - resting appearance, `--color-action-primary` surface,
  `--color-action-on-primary` label.
- hover - visibly lifted or darkened via token step, pointer cue.
- active - pressed feedback (inset or compressed), label unchanged.
- disabled - non-interactive, still legible, never color-alone cue
  (pair with reduced contrast + `aria-disabled`).
- loading - progress cue (spinner), label preserved or replaced with
  `aria-busy` announced.
- error - failed-action cue with recovery path (retry action/message
  in `--color-state-error`).
- empty - no-action slot: what renders when the action is unavailable
  (reserved space or explanatory note, no dead button).

### Secondary (alternative or dismissive actions beside primary)

- default / hover / active / disabled / loading / error / empty - same
  seven states as primary, stepped down visually (outline or muted
  surface, never competing with primary in the same block).

### Text/ghost (low-emphasis or inline actions)

- default / hover / active / disabled / loading / error / empty - same
  seven states, underline or tint on hover only, no surface shift.

## 5. Forms, modals, and feedback states

- Forms: every submit pairs with a one-line outcome note (what happens
  next). Error state uses `--color-state-error` plus text, never color
  alone. Empty state explains what to do next.
- Modals: `--color-surface-raised` + `--shadow-raised`, one primary
  action, dismiss always available (button + escape).
- Loading/empty/error patterns reuse the button-state language above
  so the whole UI speaks one dialect.

## 6. Layout

- Section order and hierarchy come from the picked wireframe; one
  primary CTA per view, above the fold, repeated after each major
  persuasion block.
- Section spacing uses `--space-section`; intra-section blocks use
  `--space-block`. No ad-hoc gaps.
- Arrangement: calm, scannable blocks; one idea per block; secondary
  CTAs stay subordinate and never share a block with primary.

## 7. Breakpoints

- Mobile-first single column, then tablet two-column, then desktop
  max-width container. Breakpoint names (values in code): `bp-tablet`,
  `bp-desktop`, `bp-wide`.
- Hero stacks on mobile (copy first, CTA immediately after); pricing
  and grids collapse to one card per row; nav collapses to a single
  menu control below `bp-tablet`.
- No horizontal scroll at any breakpoint; touch targets stay usable
  on the smallest breakpoint.

## 8. Backgrounds, 3D, aesthetic, arrangement

- Backgrounds: flat `--color-surface-primary` with
  `--color-surface-raised` panels; no gradients unless the picked
  direction explicitly keeps one (record here if so).
- 3D: V1 keeps flat or subtle depth via `--shadow-raised` only.
- Aesthetic and arrangement follow the picked direction and the green
  verdicts in `design-feedback.md`; deviations are recorded in the
  direction summary above.

## 9. Animation notes (V1 scope)

- Opportunity-scan only: list where motion could help later (hero
  entrance, CTA hover, modal open) without implementing timelines.
- Reduced-motion: every animation ships a `reduced-motion` fallback
  (instant state change, no parallax, no autoplay).
- Performance guards: transform/opacity only, no layout-thrashing
  properties, lazy or deferred heavy effects. Full choreography
  (timelines, scroll physics) is deferred past V1.

## 10. Consistency rule - check-ask-update

> **check-ask-update:** Before any future visual change, CHECK this
> `design-system.md` first. If the change deviates from it, ASK the
> user and name the deviation explicitly. On approval, UPDATE this
> file so it stays the source of truth. Never silently drift from the
> system.
