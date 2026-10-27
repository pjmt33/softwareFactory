# ADR 0004: Phase Engine (`--phase N`)

Date: 2026-10-27
Status: Accepted
Supersedes: none

## Context

RPI's `implement-outline` workflow requires phase-by-phase execution with a
human gate between phases. The factory's four gates produce a structure
outline; implementation runs one phase at a time, updates the outline's
progress markers, and stops for human confirmation.

## Decision

- `--phase N` extracts Phase N's block from `04-structure-outline.md` and
  builds an implementer prompt with the precedence rule
  (outline > design > research > ticket).
- `run_phase` runs `qwen3:8b` in a tool loop, writes to any repo path except
  `.git/`, and after the model returns, writes the updated phase block back
  to the outline (checkbox `[x]` marks persist to disk).
- The human gate prints `## Phase N Complete` with what was done and what
  manual verification remains. `y` sets the phase title to `## ✅ Phase N:`
  and commits; `n` returns feedback without committing (the outline is
  already updated with automated-verification marks).
- `--phase N --dry-run` prints the extracted block without a model call.
- Refuses if the phase title has `✅` or all checkboxes are `[x]`.

## Considered Options

1. Spawn sub-agents per phase (HumanLayer's approach). Rejected: the harness
   is single-agent Python + Ollama; there is no sub-agent runtime. The
   extended phase contract allows inline execution.
2. Auto-advance through phases without human gate. Rejected: the human gate
   is the contract's checkpoint.
3. Write the outline back only on `y`. Rejected: automated verification
   passes independently of commit; the outline should reflect that.

## Consequences

Good:
- Multi-phase features run one phase at a time; resume works because the
  outline records progress.
- The human gate is parseable (same format as HumanLayer's orchestrator).

Bad:
- The engine trusts the model's claim that automated validation passed; it
  does not re-run the commands. A future enhancement could re-execute the
  Validation section.

## Verification

- `phase-test2` and `phase-test3`: model wrote output, reported completion,
  `y` committed, outline showed `## ✅ Phase 1:` with `[x]`, second run
  returned `REFUSED: Phase 1 already marked complete`.

## Links

- Commits 2966fcc (extract + dry-run), eb0ad17 (run_phase), 921dd3e
  (outline write-back + contract gate)
- ADR 0003: RPI alignment

