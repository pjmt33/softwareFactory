# Program Design: audit visibility

## Files
- `scripts/factory.sh` — edit `audit()` only. No new files.
- Reads (does not modify) `docs/plans/<slug>/04-slices.md`.

## Types & signatures
No new shell functions. The change is an inline block inside `audit()`,
after the existing feature-plans loop:

    hdr "unchecked slices"
    open=0
    while IFS= read -r d; do
      f="$d/04-slices.md"
      [ -f "$f" ] || continue
      n=$(grep -c '^- \[ \]' "$f" 2>/dev/null || true)
      if [ "${n:-0}" -gt 0 ]; then
        printf '  %s: %s unchecked\n' "$(basename "$d")" "$n"
        open=$((open+1))
      fi
    done < <(find docs/plans -mindepth 1 -maxdepth 1 -type d | sort)
    [ "$open" -eq 0 ] && echo "  (none)"

## Call stack
1. `scripts/factory.sh audit` dispatches to the shell function `audit()`.
2. The new block runs after the existing "feature plans" section.
3. It iterates `docs/plans/*/` sorted, counts unchecked boxes per
   `04-slices.md`, and prints `<slug>: <N> unchecked` per open plan.
4. If no open plan was found, prints `(none)`.

## Test plan
1. Plan with two unchecked slices → output includes `  <slug>: 2 unchecked`.
2. Plan with all slices checked → slug absent from the section.
3. No `04-slices.md` present for a plan → that plan is skipped silently.
4. No plans at all → section prints `  (none)`.

## Least confident decisions
1. `grep -c` exits non-zero when it finds zero matches; the `|| true`
   assignment avoids `set -u` interaction. Switch to `grep -c … || echo 0`
   if the behavior differs across platforms.
2. Gate 4 approval implies `04-slices.md` exists, but the block tolerates
   a missing file via `[ -f "$f" ] || continue`.
3. `(none)` is printed whenever no open plan was counted, including when
   no plans exist at all. Alternative: distinguish "no plans" from
   "all plans complete" — not done, no current need.
