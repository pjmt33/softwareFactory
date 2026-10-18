# Product: gate-preambles

## Problem
When the model reaches Gate 2, 3, or 4, it drafts the template instead of asking first. Gate 1 was fixed with a four-question preamble; gates 2–4 are still broken the same way.

## Success metric
Zero fabricated file paths, endpoints, or signatures across three gate runs. Verified by reading each gate doc after drafting and confirming every path or signature exists in the repo or was provided by the user.

## Announcement
The software factory now asks before it drafts at every gate, not just Gate 1. Gate 2 asks which files to read; Gate 3 asks which signatures you want; Gate 4 asks you to approve the slice plan before any code runs.

## Screens
No UI. All four gates produce markdown docs in docs/plans/<feature>/. The "screen" is the doc file itself.
