#!/usr/bin/env bash
# scripts/factory.sh — local-only, read-only except for init-feature
set -o pipefail
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
