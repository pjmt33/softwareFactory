BEFORE presenting the template, propose the types and method signatures
below, then ask the user:
  1. Do these signatures match your expectations? Which should change?
  2. Are there types or files I've missed?
  3. What are the three least-confident decisions?

Do not implement bodies. Do not write any code. Present signatures only.
Do not draft the template until the user has responded to all three.

# Gate 3 — Program Design (the step everyone skips)

Read the approved product and architecture documents and inspect the relevant
code. Identify decisions still needed about changed files, interfaces, call
flows, tests, and the three least-confident decisions. Ask focused clarifying
questions in one message and wait for the user's answers before drafting; do
not repeat settled decisions or invent constraints. Save the approved draft to
`docs/plans/<slug>/03-program-design.md`.

    # Program Design: <feature name>

    ## Files
    <every file created or changed, one line each on why it lives there>

    ## Types & signatures
    <code blocks defining types and method signatures — NO implementation bodies.
    A human should read these in seconds and say "right" or "wrong.">

    ## Call stack
    <for each main flow: what calls what, top to bottom>

    ## Test plan
    <test case names and what each one asserts — before any of them exist>

    ## Least confident decisions
    <Exactly 3 items. Each must name: (a) the specific decision,
    (b) the alternative you rejected, (c) what would make you switch.
    "None" is not acceptable — if you are confident about everything,
    you have not understood the feature.>

Run the approval protocol.
