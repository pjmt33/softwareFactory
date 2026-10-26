#!/usr/bin/env bash
# scripts/factory.sh — local-only, read-only except for init-feature
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

cmd="${1:-audit}"; shift || true

red()   { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
yellow(){ printf '\033[33m%s\033[0m\n' "$*"; }
hdr()   { printf '\n== %s ==\n' "$*"; }
require() { [ -e "$1" ] || { red "MISSING: $1"; return 1; }; }

audit() {
  local fail=0
  hdr "scaffold"
  for p in SKILL.md references/status-template.md \
           references/gate-1-product.md references/gate-2-architecture.md \
           references/gate-3-program-design.md references/gate-4-vertical-slices.md \
           docs/plans docs/adr docs/external scripts; do
    require "$p" || fail=1
  done
  hdr "feature plans"
  if find docs/plans -mindepth 1 -maxdepth 1 -type d 2>/dev/null | grep -q .; then
    while IFS= read -r d; do
      printf '\n  %s\n' "$d"
      [ -f "$d/00-status.md" ] || { red "    MISSING 00-status.md"; fail=1; }
      for g in 01-product 02-architecture 03-program-design; do
        [ -f "$d/$g.md" ] || yellow "    missing $g.md (gate may not be reached)"
      done
      [ -f "$d/00-status.md" ] && grep -E '^(- )?(Gate|Slice|feature|gate-|slice-|next:)' "$d/00-status.md" | sed 's/^/    /'
      if [ -f "$d/00-status.md" ] &&
         grep -Eq '^- Gate 4 — Slice plan: APPROVED([[:space:]]|$)' "$d/00-status.md"; then
        [ -f "$d/04-slices.md" ] || {
          red "    MISSING 04-slices.md (Gate 4 is approved)"
          fail=1
        }
      fi
      if [ -f "$d/00-status.md" ] &&
         grep -Eq '^- Gate [1-4] — [^:]+: INVALIDATED' "$d/00-status.md" 2>/dev/null; then
        yellow "    gate INVALIDATED — re-approve before continuing"
      fi
    done < <(find docs/plans -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)
  else
    echo "  (no feature plans yet)"
  fi
  hdr "external refs — secret scan"
  if grep -rniE '(api[_-]?key|secret|token|password)[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9_-]{12,}' docs/external/ 2>/dev/null; then
    red "  ^ possible secret in docs/external/ — names only, never values"
    fail=1
  else
    green "  clean"
  fi
  hdr "ADR index"
  find docs/adr -maxdepth 1 -type f -name '[0-9][0-9][0-9][0-9]-*' 2>/dev/null | sort | sed 's/^/  /'
  hdr "skill hygiene"
  check_skill_inner || fail=1
  hdr "git"
  [ -d .git ] && git status --short --branch || { yellow "  not a git repo"; fail=1; }
  echo
  [ "$fail" -eq 0 ] && green "AUDIT: OK" || red "AUDIT: issues above"
  return "$fail"
}

check_skill_inner() {
  local fail=0
  [ -f SKILL.md ] || { red "  SKILL.md missing"; return 1; }
  [ -s SKILL.md ] || { red "  SKILL.md is empty"; return 1; }
  local lines; lines=$(wc -l < SKILL.md | tr -d ' ')
  if [ "$lines" -gt 80 ]; then yellow "  SKILL.md is $lines lines (target ~50)"; fail=1
  else green "  SKILL.md body: $lines lines (ok)"; fi
  if head -1 SKILL.md | grep -q '^---$'; then
    local desc; desc=$(awk '/^---$/{c++; next} c==1 && /^description:/{sub(/^description:[[:space:]]*/,""); print; exit}' SKILL.md)
    [ -n "$desc" ] && green "  description present" || { yellow "  frontmatter has no description"; fail=1; }
  else yellow "  no YAML frontmatter"; fail=1; fi
  for g in gate-1-product gate-2-architecture gate-3-program-design gate-4-vertical-slices; do
    [ -s "references/$g.md" ] && green "  references/$g.md ok" || { yellow "  references/$g.md empty or missing"; fail=1; }
  done
  for g in gate-1-product gate-2-architecture gate-3-program-design gate-4-vertical-slices; do
    grep -q "references/$g.md" SKILL.md || { yellow "  SKILL.md does not reference references/$g.md"; fail=1; }
  done
  return "$fail"
}

init_feature() {
  local slug="${1:-}"
  [ -n "$slug" ] || { red "usage: factory.sh init-feature <slug>"; exit 2; }
  if ! [[ "$slug" =~ ^[a-z][a-z0-9-]{0,63}$ ]]; then
    red "invalid slug: '$slug' — must match ^[a-z][a-z0-9-]{0,63}\$"
    exit 2
  fi
  local d="docs/plans/$slug"
  [ -e "$d" ] && { red "exists: $d"; exit 2; }
  mkdir -p "$d"
  cp references/status-template.md "$d/00-status.md"
  sed -i '' "s/<feature name>/$slug/" "$d/00-status.md"
  green "created $d/00-status.md"
}

resume() {
  hdr "resume pointers"
  find docs/plans -type f -name 00-status.md -exec sh -c 'echo "--- $1"; cat "$1"' _ {} \; 2>/dev/null || echo "  no plans yet"
  hdr "binding ADRs"
  find docs/adr -maxdepth 1 -type f -name '[0-9][0-9][0-9][0-9]-*' 2>/dev/null | sort | sed 's/^/  /'
  hdr "external refs (names only)"
  find docs/external -type f 2>/dev/null | sort | sed 's/^/  /'
  hdr "rule"
  echo "  read 00-status.md first; continue from first unapproved gate or first unchecked slice"
  echo "  do not redo an APPROVED gate unless a later gate invalidated it"
  echo "  write gate docs to disk before starting the next gate (dumb-zone rule)"
}

case "$cmd" in
  audit)        audit; exit $? ;;
  check-skill)
    hdr "skill hygiene"
    check_skill_inner; rc=$?
    echo
    [ "$rc" -eq 0 ] && green "done" || red "check-skill failed"
    exit "$rc"
    ;;
  init-feature) init_feature "${1:-}" ;;
  resume)       resume ;;
  *) echo "usage: factory.sh {audit|check-skill|init-feature <slug>|resume}"; exit 2 ;;
esac
