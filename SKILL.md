---
name: software-factory
description: Run a feature through a 4-gate approval workflow (Product, Architecture, Program Design, Vertical Slices) with persistent state in docs/plans/. Trigger when the user says "start a feature", "gate this", "run the factory", or "plan this properly". Do NOT trigger for trivial tweaks (button color, copy edits, typos) — those are exempt.
---

# Software Factory

Four gates. Stop at each until the user signs off. State lives in
`docs/plans/<feature>/00-status.md` so any fresh session resumes from disk alone.

## The four gates
1. **Product** — `references/gate-1-product.md`. User problem, success metric,
   announcement, plain HTML mockups. No tech talk.
2. **Architecture** — `references/gate-2-architecture.md`. Endpoints, data,
   query outlines, end-to-end flow, external names.
3. **Program Design** — `references/gate-3-program-design.md`. File locations,
   types and signatures (no bodies), call stack, test asserts, least confident decisions.
4. **Vertical Slices** — `references/gate-4-vertical-slices.md`. Tracer bullet first,
   then one testable slice at a time. Re-steer between slices.

## Status file
Copy `references/status-template.md` to `docs/plans/<slug>/00-status.md` before Gate 1.
Mark gates APPROVED and check slices off as you go. That file is the resume anchor.

## Approval protocol (run at every gate)
1. Write the gate doc to disk.
2. Present at most 5-10 bullet decisions plus the doc path. Do not paste the whole doc.
3. Ask exactly: "Approve Gate N, or what should change?"
4. Approval = the user clearly says yes / approve / continue. Anything else:
   revise the doc, re-ask.
5. On approval: mark the gate APPROVED in `00-status.md`, move on.
6. **Backtracking:** if a later gate reveals an earlier decision is wrong, stop,
   update the earlier doc, set that gate back to "in progress", re-approval before continuing.

## Standing rules (always on)
- **Compact at every boundary.** End of every gate and every slice: make sure the
  docs contain everything decided. Nothing important may exist only in chat.
  Tell the user it is a safe point to start a fresh session.
- **Keep diffs reviewable.** Small slices. Nudge the user to look at code at slice
  boundaries.
- **Real tests only.** Before writing a test, run it against the pre-change code.
  If it passes, the test is wrong — rewrite until it fails, then implement.
  Never comment out, skip, or weaken a test to get to green.
- **ADR permission.** If a task conflicts with an accepted ADR, stop and propose
  whether the task or the ADR should change. Do not silently work around it.
- **Artifacts.** Runnable code → `scripts/`; gate templates and knowledge →
  `references/`; plan outputs → `docs/plans/<feature>/`. Do not inline scripts
  into gate docs.
- **Durable context.** When a gate produces a decision that outlives this feature,
  offer to record it as `docs/adr/NNNN-<slug>.md` — context, decision, consequences.
  Never rewrite old ADRs; supersede them. Names-only for anything outside the
  repo goes in `docs/external/`.

## Exempt
Trivial tweaks (button color, copy edits, typos). If it fits in one commit and
one test, it does not enter the workflow.
