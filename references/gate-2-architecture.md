# Gate 2 — Architecture

Read the relevant existing code before writing this doc — never design against
an imagined codebase. Save to `docs/plans/<slug>/02-architecture.md`.

    # Architecture: <feature name>

    ## Fit
    <which existing services/modules this touches, and how>

    ## Endpoints
    <route + verb + purpose, one line each — or "none">

    ## Data
    <new or changed tables/collections, with outlines of the queries that will hit them>

    ## Flow
    <the end-to-end call order for the main path: what calls what>

    ## External
    <third-party APIs, env var NAMES (never values), webhooks — or "none">

Run the approval protocol.
