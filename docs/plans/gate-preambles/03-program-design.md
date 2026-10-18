# Program Design: gate-preambles

## Files
- `references/gate-2-architecture.md` — prepend explicit ask-first block
- `references/gate-3-program-design.md` — prepend explicit ask-first block
- `references/gate-4-vertical-slices.md` — prepend explicit ask-first block
- `docs/plans/gate-preambles/00-status.md` — mark Gates 3 and 4 APPROVED after the edits

## Types & signatures

The "type" for this feature is the preamble block. Three concrete instances, one per file. Each uses the same shape as `references/gate-1-product.md`'s preamble.

**Gate 2 preamble (verbatim):**

    BEFORE writing anything into the template, ask the user these questions,
    one message, no drafting yet:
      1. Which existing files should I read to understand the current system?
      2. What new endpoints or routes are needed, and for what?
      3. What new or changed tables/collections, and what queries will hit them?
      4. What third-party services are involved (names only, never values)?

    Do not invent answers. Read the files the user names before continuing.
    Do not draft the template until the user has answered all four.

**Gate 3 preamble (verbatim):**

    BEFORE presenting the template, propose the types and method signatures
    below, then ask the user:
      1. Do these signatures match your expectations? Which should change?
      2. Are there types or files I've missed?
      3. What are the three least-confident decisions?

    Do not implement bodies. Do not write any code. Present signatures only.
    Do not draft the template until the user has responded to all three.

**Gate 4 preamble (verbatim):**

    BEFORE any code, present the slice plan as numbered one-liners and ask:
      1. Is this the right slice order?
      2. Should slice 1 be smaller or larger?
      3. Any slices missing or wrongly grouped?

    Do not start coding until the slice plan is approved.

## Call stack
None — documentation edit. For each file: read, prepend block, write, verify.

## Test plan
- test-gate-2-preamble: head -10 references/gate-2-architecture.md shows the four numbered questions above
- test-gate-3-preamble: head -12 references/gate-3-program-design.md shows the three numbered questions above
- test-gate-4-preamble: head -12 references/gate-4-vertical-slices.md shows the three numbered questions above

All three must pass before Gate 4 is marked APPROVED. `./scripts/factory.sh check-skill` must also still pass.

## Least confident decisions
1. Number of questions per gate. Gate 1 has four; gates 2-4 have three or four above. Alternative: standardize at exactly four. Would switch if a future gate needs more or fewer, or if symmetry matters for the model.
2. Whether to keep the existing descriptive text below the new preamble. Decision: keep it (additive, not replacement). Alternative: remove descriptive text to avoid competing instructions. Would switch if the model ignores the preamble and follows the descriptive text instead - the same failure mode observed in this session.
3. Where the preamble goes in Gate 4. Decision: at the top, before the slice rules. Alternative: after the slice rules, immediately before the write-the-slice-plan instruction. Would switch if the model reads only the first N tokens and misses the preamble.
