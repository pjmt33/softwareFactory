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
