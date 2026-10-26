# Software Factory — local, test-build posture

A 4-gate feature workflow (Product -> Architecture -> Program Design -> Vertical
Slices) implemented as a SKILL.md-compatible skill. State lives in
`docs/plans/<feature>/00-status.md` so any fresh session can resume from disk
alone.

- **Operator guide:** [MANUAL.md](MANUAL.md) — canonical commands, plan layout,
  diagnostics, boundaries.
- **Agent behavior:** [SKILL.md](SKILL.md) and [references/](references/) — the
  four gates, approval protocol, standing rules.
- **History:** [docs/history/setup-log.md](docs/history/setup-log.md) — archived
  setup narrative; not current instructions.

## Lanes (do not mix)
- This repo: the factory skill, its templates, its audit script, and plan outputs.
- `docs/external/`: **names only** for anything outside this repo (env var NAMES,
  endpoint paths, model IDs, dashboard URLs). Never values, never secrets.
- The officeLab MCP/RAG system is referenced from `docs/external/` only.
  It is not configured, imported, or invoked from here.

## Quick start

    scripts/factory.sh resume
    scripts/factory.sh init-feature <slug>
    python3 harness.py references/gate-2-architecture.md docs/plans/<slug>/00-status.md "Gate 2 is pending."

Commands, the resume contract, gate approval, and the harness sandbox are all
documented in [MANUAL.md](MANUAL.md) and [SKILL.md](SKILL.md). This file does
not restate them.
