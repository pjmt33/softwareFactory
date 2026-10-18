# Product: gate-preambles

## Problem
Gates 2, 3, and 4 have descriptive ask-first language ("ask focused clarifying
questions...") but not explicit, numbered questions like Gate 1 has. In practice,
small models ignore the descriptive guidance and invent file paths, endpoints,
and signatures. Gate 1's four explicit numbered questions work; gates 2–4 don't
have equivalents.

## Success metric
Zero fabricated file paths, endpoints, or signatures across three consecutive
gate runs at Gates 2, 3, and 4. Verified by reading each gate doc after drafting
and confirming every path or signature exists in the repo or was provided by
the user.

## Announcement
The software factory now asks explicit, numbered questions at every gate, not
just Gate 1. Gate 2 asks "which files should I read?" — not "identify missing
decisions." Gate 3 asks "which signatures do you want?" — not "identify
decisions still needed." Gate 4 asks "approve this slice plan?" — not "ask
focused questions." Same explicit pattern as Gate 1, applied to the three
remaining gates.

## Screens
No UI. All four gates produce markdown docs in docs/plans/<feature>/. The
"screen" is the doc file itself.
