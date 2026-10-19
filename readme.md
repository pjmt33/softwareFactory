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
Run `harness.py ... --answer-file answers.txt` to read gate answers from a file instead of typing them.
# softwareFactory
# softwareFactory
# softwareFactory

## Running a gate

The harness executes one gate at a time. It reads the gate reference, asks the
gate's questions, and writes the artifact to `docs/plans/<slug>/`.

    python3 harness.py references/gate-2-architecture.md docs/plans/<slug>/00-status.md "Gate 2 is pending. The slug is <slug>."

To read gate answers from a file instead of typing:

    python3 harness.py references/gate-2-architecture.md docs/plans/<slug>/00-status.md "..." --answer-file answers.txt

The harness sandboxes reads to `references/` and `docs/plans/`, and writes to
`docs/plans/` only. It will not overwrite an approved gate's artifact. A startup
probe confirms the model can return structured tool calls before the gate runs.

## The four gates

1. Product — `docs/plans/<slug>/01-product.md`
2. Architecture — `docs/plans/<slug>/02-architecture.md`
3. Program Design — `docs/plans/<slug>/03-program-design.md`
4. Slice plan — `docs/plans/<slug>/04-slices.md`

Approval is manual: review the artifact, then edit the gate's line in
`docs/plans/<slug>/00-status.md` to `APPROVED <date>`.
