# Questionnaire

A few quick questions first. Ask these before collecting examples. Keep it fast: one-line answers
are fine. Do not proceed to collect and rank until all answers plus
links below are in hand.

## The 5 quick questions

1. In 3 words, what feeling should the site give? (e.g. calm, bold, playful)
2. Who is it for, and what should they do first? (audience + primary action)
3. Bold and memorable, or calm and trustworthy, which way, and where?
4. Any brand constraints? (colors, fonts, logo, must-avoid styles)
5. Which section matters most if only one can shine? (hero, pricing, gallery...)

## Liked examples (2-3 links)

- Link 1:
- What specifically do you like about it? (name the part: hero, buttons, color...)
- Link 2:
- What specifically do you like about it?
- Link 3 (optional):
- What specifically do you like about it?

## Disliked example (1 link + why)

- Link:
- Why does it not work for you? (say exactly what to avoid)

## Handoff

Feed the answers + links into scripts/collect.py. It records a one-line verdict for each fixed part, in fixed order, into ranked-parts.json. Pass systemdesignhunt picks as `sources` in the input JSON. Any link that
cannot be fetched falls back to assets/curated-defaults.md, and the
fallback is noted explicitly.
