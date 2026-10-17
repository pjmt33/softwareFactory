# Gate 3 — Program Design (the step everyone skips)

The decisions the agent would otherwise make silently mid-implementation.
Save to `docs/plans/<slug>/03-program-design.md`.

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
