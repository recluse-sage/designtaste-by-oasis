# Sub-skills (external first, inline fallback)

Prefer an installed external skill when present. Otherwise use the inline reference. Never invent install commands for these skills.

| Phase | Prefer first (if installed) | Inline fallback |
| --- | --- | --- |
| Anti-slop direction check | `design-taste-frontend` | `references/taste.md` |
| Marketing and UX copy | Installed copywriting skill (match by description containing 'copywriting', any name) | `references/copy-slim.md` |
| Post-pick build and ship | Installed ship skill (match description containing 'ship' or 'product pipeline', e.g. `ship-product-pipeline`) | Stop at `design-system.md` handoff, no build |

## Rules

- If an external skill below is installed, invoke it by name first.
- Match copy and ship skills by description text, not by assumed name.
- Only `design-taste-frontend` and the ship example use fixed names here.
- Do not add install steps or registry commands.
- Fallbacks keep the run inside this skill with no extra deps.

## Notes

- Check installed skills by listing names plus descriptions.
- Use the first match when several copy or ship skills exist.
- Record which path was used: external name or inline fallback.
- Keep wireframes and feedback inside this run when falling back.
