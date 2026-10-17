# Gate 1 — Product (no tech talk)

Work with the user to fill this template. Save to `docs/plans/<slug>/01-product.md`.

    # Product: <feature name>

    ## Problem
    <the user problem, in the end-user's words — not the developer's>

    ## Success metric
    <one real number tied to the business, and how it's measured>

    ## Announcement — the blog post before the feature
    <3-6 sentences announcing this feature to users. If you can't write it,
    you're building the wrong thing.>

    ## Screens
    <one line per mockup file in ./mockups/ — or "no UI">

Rules:
- Banned in this stage: databases, schemas, endpoints, architecture, file names.
  If tech appears, move it to Gate 2.
- For anything with a UI: one plain HTML file per screen in `mockups/` —
  no framework, no build step, throwaway by design. Iterate until the user
  says "yes, that."
- Run the approval protocol.
