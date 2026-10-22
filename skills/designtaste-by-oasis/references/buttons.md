# Buttons

You set how buttons look and act. Define the core button set with all states. V1 covers the core set
only: primary, secondary, and text/ghost. No icon system here.

## Core set

- Primary: the single main action per view.
- Secondary: alternative or dismissive actions beside primary.
- Text/ghost: low-emphasis or inline actions.

## All states (required for each core variant)

- default - resting appearance and label style.
- hover - visible change on pointer hover.
- active - pressed feedback.
- disabled - non-interactive, still legible, never relies on color alone.
- loading - progress cue, label preserved or replaced by spinner + aria-busy.
- error - failed-action cue with recovery path (retry / message).
- empty - no-action slot: what renders when the action is unavailable.

## Rules

- One primary per view; everything else steps down.
- Every variant ships all seven states above; a missing state is a
  defect.
- Keep labels verb-first, 1-3 words.

## Output

A compact matrix: 3 variants x 7 states with one-line behavior
each. Short enough to paste into the wireframe build.
