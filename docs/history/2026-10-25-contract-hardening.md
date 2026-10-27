# 2026-10-25 — contract hardening

- harness: approval guard now keyed to the artifact's own gate (was: any
  `APPROVED` string locked the whole plan dir)
- status-template: concrete default states + `INVALIDATED` vocabulary;
  `init-feature` no longer emits a menu line
- factory.sh audit: surfaces `INVALIDATED` gates
- SKILL.md: stop-after-ask moved to preface; backtracking has a defined
  on-disk state change
- harness: `--answer-file` accepts optional `# gate-N` header; mismatched
  header aborts
- SKILL.md: slice-done defined; test-failure escape hatch added
- docs: README deduped against MANUAL; `### Sync` subsection; answer-file note

# 2026-10-25 — contract hardening

- harness: approval guard keyed to the artifact's own gate (was: any
  `APPROVED` string locked the whole plan dir), and moved above the
  `f.exists()` short-circuit so re-creating an approved artifact is rejected
  too (second bug found by end-to-end test)
- status-template: concrete default states + `INVALIDATED` vocabulary;
  `init-feature` no longer emits a menu line
- factory.sh audit: surfaces `INVALIDATED` gates
- SKILL.md: stop-after-ask moved to preface; backtracking has a defined
  on-disk state change
- harness: `--answer-file` accepts optional `# gate-N` header; mismatched
  header aborts
- SKILL.md: slice-done defined; test-failure escape hatch added
- docs: README deduped against MANUAL; `### Sync` subsection; answer-file note
- verified end-to-end: REJECTED for approved-gate artifact (even if absent),
  Wrote for unapproved later gate, Wrote for non-gated status file, audit
  surfaces INVALIDATED, answer-file gate mismatch aborts, template has no
  menu pipes
- `_smoke-test` left as-is: intentional "do not advance" artifact; slug
  validator rejects leading underscore so it cannot be regenerated
- RPI restructure (58ecce7): gates renamed to Questions/Research/Design
  Discussion/Structure Outline; research isolated from ticket via
  harness.RPI_READS. Existing plan dirs (first-feature, gate-preambles,
  harness-answer-file, harness-readme, _smoke-test) retain old gate labels
  and are not validated by the new Gate 4 check — historical record, no
  migration.
