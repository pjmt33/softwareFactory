# Software Factory — local, test-build posture

A 4-gate feature workflow (Product → Architecture → Program Design → Vertical Slices)
implemented as a SKILL.md-compatible skill. State lives in `docs/plans/<feature>/00-status.md`
so any fresh session can resume from disk alone.

See [MANUAL.md](MANUAL.md) for the canonical operator guide. The historical
setup and troubleshooting narrative is archived in `docs/history/setup-log.md`;
it is not a source of current workflow instructions.

## Lanes (do not mix)
- This repo: the factory skill, its templates, its audit script, and plan outputs.
- `docs/external/`: **names only** for anything outside this repo (env var NAMES,
  endpoint paths, model IDs, dashboard URLs). Never values, never secrets.
- The officeLab MCP/RAG system is referenced from `docs/external/` only.
  It is not configured, imported, or invoked from here.

## Resume contract
At the start of any session that touches a feature: if `docs/plans/<slug>/00-status.md`
exists, read every doc in that folder first, then continue from the first unapproved
gate or first unchecked slice. Never redo an APPROVED gate unless the user asks or a
later gate invalidated it.

## Trivial tweaks are exempt
Button color, copy edits, typo fixes — no gates. If a "feature" fits in one commit
and one test, it does not enter the workflow.

## Commands
    scripts/factory.sh audit          # read-only: scaffold, drift, secrets, ADRs, skill hygiene
    scripts/factory.sh check-skill    # progressive-disclosure hygiene on SKILL.md + gate refs
    scripts/factory.sh init-feature <slug>
    scripts/factory.sh resume         # what a fresh session should read first
