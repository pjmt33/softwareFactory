- Files (grouped by purpose, paths only)
  - Implementation: scripts/factory.sh
  - Config: references/status-template.md, docs/plans/*/00-status.md
  - Types: (none explicitly defined)

- Patterns (with file:line references)
  1. `find` loop for plan directories: scripts/factory.sh:23
  2. Status file format: references/status-template.md:1
  3. `hdr/echo/printf` formatting: scripts/factory.sh:15
  4. `case "$1";` dispatch: scripts/factory.sh:45
  5. "next -> Gate N" rendering: scripts/factory.sh:30

- Test coverage (what exists, what's asserted)
  - No automated tests for factory.sh
  - Manual verification of resume() output in resume-next-gate
  - No assertions in test coverage

- Dependencies (names only)
  - Internal tools: find, grep, sed, basename
  - Status file format: - Gate N — Label: STATE

- Open questions (things you could not determine from code alone)
  - How is the status file format enforced?
  - Are there additional manual verification steps beyond resume-next-gate?