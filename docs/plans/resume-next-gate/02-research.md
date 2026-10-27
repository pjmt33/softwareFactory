- Files (grouped by purpose, paths only)
  - Implementation: scripts/factory.sh, docs/plans/*/00-status.md, references/status-template.md
  - Tests: none
  - Config: references/status-template.md
  - Types: none

- Patterns (with file:line references)
  - grep -Eq '^- Gate N — Label: STATE' (scripts/factory.sh:audit())
  - find docs/plans -mindepth 1 -maxdepth 1 -type d (scripts/factory.sh:audit(), resume())
  - sed -E (scripts/factory.sh:init_feature())
  - printf/echo (scripts/factory.sh:hdr(), green(), yellow())
  - process substitution < <(find ...) (scripts/factory.sh:audit() unchecked-slices loop)

- Test coverage (what exists, what's asserted)
  - No automated tests for factory.sh
  - resume() performs file operations but lacks assertions

- Dependencies (names only)
  - 00-status.md file format
  - Status line pattern: '- Gate N — Label: STATE' (STATE: pending/in progress/APPROVED/INVALIDATED)

- Open questions
  - No tests for file operations in resume()
  - No explicit assertions for status file parsing