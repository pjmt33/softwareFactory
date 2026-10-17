# Software Factory Agent Instructions

You are working inside a 4-gate feature workflow.

## Read first
1. `readme.md` — lane rules and resume contract
2. `SKILL.md` — the four gates and approval protocol
3. `docs/plans/<feature>/00-status.md` — current gate state

## Gate 1 behavior
- Ask the four questions from `references/gate-1-product.md` BEFORE drafting.
- Do not invent answers.
- Do not narrate what you are about to do. Ask the questions.
- After the user answers, write `01-product.md` using only their words.
- Present 5-10 bullet decisions and ask exactly: "Approve Gate 1, or what should change?"
- Stop. Do not proceed to Gate 2.

## Hard rules
- Trivial tweaks are exempt (button color, copy edits, typos).
- Never write code during Gates 1-3.
- If a task conflicts with an accepted ADR, stop and propose whether the task or the ADR should change.

