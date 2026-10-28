## Phase 1: parse --all flag and list all plans
Files: scripts/factory.sh
Change:
1. In the `case "$cmd" in` dispatch, change `resume)       resume ;;` to `resume)       resume "$@" ;;`.
2. At the top of `resume()` (after `resume() {`), add:
   `local all=0`
   `[ "${1:-}" = "--all" ] && all=1`
3. After `[ "$any" -eq 0 ] && echo "  (none)"`, add:
   if [ "$all" -eq 1 ]; then
     while IFS= read -r d; do
       slug=$(basename "$d")
       case "$slug" in _*) continue;; esac
       if [ -f "$d/00-status.md" ] &&
          ! grep -Eq '^- Gate [1-4] — [^:]+: (pending|in progress|INVALIDATED)' "$d/00-status.md" 2>/dev/null; then
         printf '  %s: all gates approved\n' "$slug"
       fi
     done < <(find docs/plans -mindepth 1 -maxdepth 1 -type d | sort)
   fi
Validation: `test "$(scripts/factory.sh resume --all | grep -c 'all gates approved')" -ge 5` AND `test "$(scripts/factory.sh resume | grep -c 'next ->')" -eq 0`
- [x] resume --all lists all plans
- [x] resume without --all unchanged

## Phase 2: test the three cases
Files: scripts/factory.sh, /tmp/resume-all-test/
Validation: (a) all plans approved → each line ends `all gates approved`; (b) one plan open → that plan shows `next -> Gate N`; (c) no plans → prints `(none)`.
- [ ] case a: all approved
- [ ] case b: one open
- [ ] case c: no plans

STATUS:
# Status: resume-all

<!--
Gate states (the only legal values):
  pending
  in progress
  APPROVED <YYYY-MM-DD>
  INVALIDATED <YYYY-MM-DD> by gate-N
Slices are checkboxes; a slice is done when it has one commit, one test that failed before the change and passes after, and its box is checked.
-->

- Gate 1 — Questions: APPROVED 2026-10-27
- Gate 2 — Research: APPROVED 2026-10-27
- Gate 3 — Design Discussion: APPROVED 2026-10-27
- Gate 4 — Structure Outline: pending

## Slices
- [ ] Slice 1 — tracer bullet: <one line>
- [ ] Slice 2 — <one line>

## Notes for a fresh session
<anything decided in chat that a new session must know>

APPROVED PRIOR GATES (do not contradict these):
=== 02-research.md ===
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

=== 03-design-discussion.md ===
# Design Discussion — Desired State

## Current state (from research, with references)
- `resume()` prints a "next gates" section listing open plans only (scripts/factory.sh:30)
- Plans with all gates APPROVED are skipped
- No `--all` flag exists
- No inventory of approved plans

## Desired end state
`resume --all` lists every plan directory with its status:
- `<slug>: next -> Gate N (Label)` for open plans
- `<slug>: all gates approved` for fully-approved plans
`resume` without `--all` keeps current behavior

## Design choices
1. **Flag parsing**:
   - Option A: `case "$1" in --all) ...` (matches existing dispatch style: scripts/factory.sh:45)
   - Option B: `getopts`
   - Recommendation: `case` for consistency with current pattern

2. **Output format**:
   - Same `<slug>: ...` shape
   - Use `all gates approved` as status line for approved plans
   - Recommendation: minimal new vocabulary, consistent with status file format (references/status-template.md:1)

3. **Which plans to include**:
   - Option C: Every plan dir with `00-status.md` (audited in `resume-next-gate`)
   - Recommendation: All dirs, since audit already validates `00-status.md` exists

## Resolved decisions
- Case-based flag parsing
- Same output shape
- All plans included

## Open questions
none

TASK:
Gate 4 is pending. The slug is resume-all.

Prior gate artifacts are already included above; do not read them again. Tools: read_file, write_file. RULE: ask your clarifying questions BEFORE calling write_file. Do not re-read a file you already read. If you call write_file before asking, it will be rejected.

