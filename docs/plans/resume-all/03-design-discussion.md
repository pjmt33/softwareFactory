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