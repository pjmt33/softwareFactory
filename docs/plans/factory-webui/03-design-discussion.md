## Current state (from research, with references)
- factory.sh is a CLI; no web layer (research: `scripts/factory.sh:XX`)
- resume --all prints plain text (research: `scripts/factory.sh:XX`)
- 00-status.md is the state (research: `docs/plans/*/00-status.md:XX`)
- 04-structure-outline.md has phase checkboxes (research: `docs/plans/*/04-structure-outline.md:XX`)
- No JSON output (research: patterns across files)

## Desired end state
A single local web page, read-only, that lists every plan with its next gate or "all gates approved" and its phase checkboxes, served by a minimal Python HTTP server on localhost.

## Design choices
1. **Framework**: Flask vs Python stdlib http.server
   - Recommendation: stdlib http.server
   - Why: Adds no dependency; the page is one route

2. **Data source**: Parse 00-status.md and 04-structure-outline.md directly in Python vs call factory.sh resume --all and parse its output
   - Recommendation: Parse files directly
   - Why: resume --all output is human-formatted and may change; files are source of truth

3. **Read-only vs execution**: Read-only only in Phase 1 vs allow execution (--phase N)
   - Recommendation: Read-only
   - Why: Execution must preserve the human gate

## Resolved decisions
- stdlib http.server
- Parse files directly
- Read-only

## Open questions
none