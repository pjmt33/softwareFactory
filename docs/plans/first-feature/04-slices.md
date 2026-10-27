# Slices: audit visibility

- [ ] Slice 1 — tracer bullet: add `hdr "unchecked slices"` to `audit()`,
      with no loop; it always prints `  (none)` and exits 0. Test: run
      `scripts/factory.sh audit` and assert the output contains
      `== unchecked slices ==` followed by `  (none)`, exit code 0.
- [ ] Slice 2 — counting loop: iterate `docs/plans/*/04-slices.md`, count
      `^- \[ \]` lines, print `  <slug>: N unchecked` per open plan; print
      `  (none)` if no open plans. Test: plan with 2 unchecked prints the
      line; fully-checked plan absent; no plans prints `  (none)`.
