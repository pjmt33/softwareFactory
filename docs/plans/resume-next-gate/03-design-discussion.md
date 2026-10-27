- Current state (from research, with references)
  - resume() currently runs three find/cat blocks (00-status.md files, docs/adr, docs/external) then prints three rule lines. No gate-state parsing; no plan-aware output. No automated tests exist for factory.sh.
- Desired end state
  - resume() additionally parses each 00-status.md and prints "<slug>: next -> Gate N (Label)" for the first gate line that is not APPROVED (i.e. pending, in progress, or INVALIDATED). Plans where all four gates are APPROVED are omitted. If no plan has an open gate, print "  (none)". Raw 00-status.md dumping is removed.
- Design choices (2–3, each with options and recommendation)
  1. Parsing: grep -E '^- Gate [1-4] — [^:]+: (pending|in progress|INVALIDATED)' | head -1, vs a sed loop. Recommendation: grep, because audit() already uses the same pattern for Gate 4 (scripts/factory.sh:audit()).
  2. Output format: single line per plan, left-aligned, vs a table. Recommendation: single line, consistent with existing hdr/echo/printf style (scripts/factory.sh:hdr()).
  3. Plans with all gates APPROVED: omit vs print "(all approved)". Recommendation: omit, matches product success metric.
- Resolved decisions
  - grep-based parse, single-line output, omit fully-approved plans, remove raw cat dump.
- Open questions (must be empty or explicitly deferred)
  - none