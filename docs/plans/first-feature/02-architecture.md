# Architecture: audit visibility

## Fit
Touches the factory.sh audit script and slices management in docs/plans/<slug>/04-slices.md.

## Endpoints
`factory.sh audit` gains a "== unchecked slices ==" section listing plan slugs with unchecked boxes.

## Data
Reads docs/plans/<slug>/04-slices.md; counts lines matching "^- \[ \]" (unchecked).
A plan is "open" if unchecked > 0 and 04-slices.md exists. Checked-box count is
not needed — the success metric is "fully-checked plans do not appear," which
falls out of unchecked == 0.

## Flow
After the existing "feature plans" section, iterate plan dirs: if open, print "  <slug>: <N> unchecked"; if no plan is open, print "  (none)".

## External
none
