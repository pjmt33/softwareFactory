BEFORE any code, present the slice plan as numbered one-liners and ask:
  1. Is this the right slice order?
  2. Should slice 1 be smaller or larger?
  3. Any slices missing or wrongly grouped?

Do not start coding until the slice plan is approved.

# Gate 4 — Vertical Slices (tracer bullets)

Read the approved product, architecture, and program-design documents, plus the
current status and relevant code. Before planning, ask focused questions about
acceptance, test/run commands, dependencies, and slice boundaries in one
message; wait for the user's answers and do not invent constraints. Then write
the slice plan as `04-slices.md` — one line per slice, in build order — and run
the approval protocol on it. Implement only after Gate 4 is approved.

## Slice rules
- Slice 1 is the tracer bullet: a mocked/hardcoded endpoint and a stubbed UI
  (or curl-able response), wired end to end. It does almost nothing — but it runs,
  and the user can see it.
- Slice 2: replace mocks with the real logic for the single happy path.
- Slice 3+: one capability per slice — a business rule, error handling, an edge case,
  polish — each ending in a working, testable state.
- Banned: horizontal building (all the database, then all services, then all API,
  then all frontend, with nothing testable until the end).

## After every slice
- Prove it works — run it, curl it, or browser-test it, and show the user the result.
- Check the slice off in `00-status.md`.
- Ask: "Continue to slice N+1, or re-steer?" If the trajectory is wrong, fix
  direction before adding more code.
