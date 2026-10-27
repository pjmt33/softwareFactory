# ADR 0003: RPI Alignment — Gate Restructure and Research Isolation

Date: 2026-10-27
Status: Accepted
Supersedes: none

## Context

The factory's four gates were Product/Architecture/Program Design/Slices.
HumanLayer's RPI workflow separates research from design and isolates research
from the ticket to avoid confirmation bias. The factory needed to adopt this
structure without installing HumanLayer's runtime.

## Decision

- Renamed gates to Questions/Research/Design Discussion/Structure Outline.
- Added `RPI_READS` in `harness.py` so Gate 2 (Research) sees no prior
  artifacts, Gate 3 (Design) sees only Gate 2, Gate 4 (Outline) sees Gates 2
  and 3.
- Artifact filenames: `01-product.md`, `02-research.md`,
  `03-design-discussion.md`, `04-structure-outline.md`.
- `audit()` checks for the RPI artifact names.

## Evidence

Both `first-feature` and `resume-next-gate` ran through the new gates.
Research artifacts contained no design recommendations; design artifacts cited
research `file:line` references. The isolation held in both runs.

## Consequences

Good:
- Research is genuinely fact-finding, not opinionated by the ticket.
- Design choices are grounded in documented patterns.
- Artifact contracts match HumanLayer's RPI structure, easing future
  integration.

Bad:
- Old plan dirs (`first-feature`, `gate-preambles`, `harness-answer-file`,
  `harness-readme`, `_smoke-test`) keep old gate labels and show yellow
  `missing 02-research.md` warnings in audit. Historical record, no migration.
- The Gate 4 check now looks for `04-structure-outline.md`; old plans with
  `04-slices.md` are not validated.

## Links

- Commit 58ecce7: RPI gate restructure
- Commit f025943: audit RPI artifact names + resume restore
- `docs/plans/first-feature/`, `docs/plans/resume-next-gate/`
