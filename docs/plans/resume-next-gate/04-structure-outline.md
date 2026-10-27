## Phase 1: Add next gates section
Files: scripts/factory.sh, docs/plans/*/*.md
Validation: resume-next-gate has Gates 1-3 APPROVED, Gate 4 pending → output contains "resume-next-gate: next -> Gate 4 (Structure Outline)"; a scratch plan all-APPROVED does not appear; after all plans approved, prints "  (none)"
- [x] resume-next-gate printed at Gate 4
- [x] scratch all-APPROVED plan omitted
- [x] (none) when no open gates

## Phase 2: Cleanup old status dumps
Files: scripts/factory.sh
Validation: resume output contains "== next gates ==" section; no raw "# Status:" dumps appear; audit still passes.
- [x] no raw "# Status:" in resume output
- [x] audit passes
