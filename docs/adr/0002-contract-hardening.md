# ADR 0002: Contract hardening — gate-scoped guard and INVALIDATED state

Date: 2026-10-26
Status: Accepted
Supersedes: none

## Context

After ADR 0001 established the thin harness, an audit of the three enforcement
contracts (SKILL.md, references/status-template.md, harness.py + factory.sh)
found four defects:

1. `harness.wf()` rejected any write to a plan directory if the string
   "APPROVED" appeared anywhere in `00-status.md`. This blocked revising an
   unapproved later gate after an earlier gate was approved, and blocked
   writing `00-status.md` itself.
2. The guard was inside `if f.exists():`, so an approved gate's artifact could
   be re-created from scratch (not-yet-existing file skipped the check).
3. `status-template.md` shipped a menu line (`pending | in progress | APPROVED
   <date>`), so a fresh session could not read gate state from disk. There was
   no `INVALIDATED` state, so backtracking could not be detected on resume.
4. `--answer-file` consumed lines with no binding to gate or date; a stale
   file silently answered the wrong gate.

## Decision

- `wf()` maps `NN-*.md` to gate N and rejects only if **that gate's** line is
  `APPROVED`. The check runs **before** the `f.exists()` branch; non-gated
  files (`00-status.md`, `mockups/`) are unrestricted.
- `status-template.md` emits one concrete state per gate (`pending`) and
  documents the legal states: `pending`, `in progress`, `APPROVED <date>`,
  `INVALIDATED <date> by gate-N`.
- `factory.sh audit` prints a warning for any `INVALIDATED` gate line.
- `--answer-file` accepts an optional first line `# gate-N`; if present and
  it does not match the gate reference, the harness aborts before the probe.
  Headerless files remain accepted (backwards compatible); MANUAL documents
  answer files as single-use.

## Considered Options

1. Keep the broad guard (any APPROVED locks the dir). Rejected: makes
   backtracking and status edits impossible without manual `sed`.
2. Require `# gate-N` header on every answer file. Rejected: breaks existing
   answer files; optional header catches the real risk (wrong gate) without a
   migration.
3. Add `INVALIDATED` as a status value vs. keep backtracking as "in progress".
   Chosen: `INVALIDATED` is machine-detectable from disk, matching the resume
   contract ("never redo an APPROVED gate unless a later gate invalidated it").

## Consequences

Good:
- Backtracking is possible and detectable from disk alone; a fresh session
  reads `INVALIDATED` and knows to re-approve.
- Approved artifacts cannot be overwritten or re-created.
- Wrong-gate answer files abort before the model is called.

Bad:
- Headerless reused answer files still silently re-consume lines; documented
  as single-use, not enforced.
- `gate_approved` depends on the exact status line shape (`- Gate N — Label:
  APPROVED …`); a hand-edited variant could evade detection.

Neutral:
- The guard now runs for every `wf()` call, including not-yet-existing files;
  the only cost is one extra file read of `00-status.md` per write.

## Verification

End-to-end (2026-10-26, `contract-test` slug, since deleted):
- Gate 1 APPROVED, `wf("…/01-product.md")` → REJECTED (even with no existing file).
- Gate 2 pending, `wf("…/02-architecture.md")` → Wrote.
- `wf("…/00-status.md")` → Wrote (non-gated).
- Gate 1 INVALIDATED → `factory.sh audit` prints the warning.
- `--answer-file` with `# gate-3` against gate-2 ref → ABORT before probe.
- `init-feature` output has zero `|` characters.

## Links

- Commits: f7b55e5 (guard scope, states, backtracking, answer-file check),
  d0fba04 (guard above `exists()`)
- Log: docs/history/2026-10-25-contract-hardening.md
- ADR 0001: thin harness
