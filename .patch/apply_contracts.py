#!/usr/bin/env python3
"""Apply the four contract fixes in place. Refuses on anchor mismatch."""
from pathlib import Path
import sys

R = Path(__file__).resolve().parent.parent  # repo root

def replace_once(text, old, new, label):
    if text.count(old) != 1:
        sys.exit(f"ABORT: anchor for {label} found {text.count(old)} times (need 1)")
    return text.replace(old, new)

# ---------- 1. harness.py ----------
p = R / "harness.py"
t = p.read_text(encoding="utf-8")

old_wf = '''def wf(path, content):
    f = (R / path).resolve()
    plans = (R / "docs" / "plans").resolve()
    if plans not in f.parents:
        return f"REJECTED: writes limited to docs/plans/. Got {path}"
    if f.exists():
        status = (f.parent / "00-status.md")
        if status.exists() and "APPROVED" in status.read_text(encoding="utf-8"):
            return f"REJECTED: {path} belongs to an approved gate; will not overwrite."
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} bytes to {path}"'''

new_wf = '''GATE_BY_PREFIX = {"01": 1, "02": 2, "03": 3, "04": 4}

def gate_of(path):
    """Gate number for an artifact path, or None if not a gated artifact."""
    name = Path(path).name
    return GATE_BY_PREFIX.get(name[:2]) if name[:2] in GATE_BY_PREFIX else None

def gate_approved(status_text, gate_num):
    """True iff the specific gate line is APPROVED."""
    pat = re.compile(r"^- Gate\\s+%d\\b[^\\n]*:\\s*APPROVED(\\s|$)" % gate_num, re.M)
    return bool(pat.search(status_text))

def wf(path, content):
    f = (R / path).resolve()
    plans = (R / "docs" / "plans").resolve()
    if plans not in f.parents:
        return f"REJECTED: writes limited to docs/plans/. Got {path}"
    if f.exists():
        status = f.parent / "00-status.md"
        g = gate_of(f)
        if g and status.exists() and gate_approved(status.read_text(encoding="utf-8"), g):
            return f"REJECTED: {path} belongs to approved Gate {g}; will not overwrite."
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} bytes to {path}"'''

t = replace_once(t, old_wf, new_wf, "harness.wf")

old_af = '''    if "--answer-file" in args:
        idx = args.index("--answer-file")
        path = args[idx + 1]
        ANSWER_LINES.extend(Path(path).read_text(encoding="utf-8").splitlines())
        del args[idx:idx + 2]'''

new_af = '''    if "--answer-file" in args:
        idx = args.index("--answer-file")
        path = args[idx + 1]
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        expected = None
        if lines and lines[0].startswith("#"):
            m = re.match(r"#\\s*gate-(\\d)\\b", lines[0].strip())
            if not m:
                print(f"ABORT: {path} header must be '# gate-N'. Got: {lines[0]!r}",
                      file=sys.stderr)
                sys.exit(2)
            expected = int(m.group(1))
            lines = lines[1:]
        gate_arg = next((a for a in args if "gate-" in a), "")
        gm = re.search(r"gate-(\\d)", gate_arg)
        actual = int(gm.group(1)) if gm else None
        if expected is not None and actual is not None and expected != actual:
            print(f"ABORT: answer file is for gate {expected}, "
                  f"but gate ref is gate {actual}.", file=sys.stderr)
            sys.exit(2)
        ANSWER_LINES.extend(lines)
        del args[idx:idx + 2]'''

t = replace_once(t, old_af, new_af, "harness.answer_file")
p.write_text(t, encoding="utf-8")
print("OK harness.py")

# ---------- 2. references/status-template.md (whole-file rewrite) ----------
p = R / "references" / "status-template.md"
p.write_text('''# Status: <feature name>

<!--
Gate states (the only legal values):
  pending
  in progress
  APPROVED <YYYY-MM-DD>
  INVALIDATED <YYYY-MM-DD> by gate-N
Slices are checkboxes; a slice is done when it has one commit, one test that
failed before the change and passes after, and its box is checked.
-->

- Gate 1 — Product: pending
- Gate 2 — Architecture: pending
- Gate 3 — Program Design: pending
- Gate 4 — Slice plan: pending

## Slices
- [ ] Slice 1 — tracer bullet: <one line>
- [ ] Slice 2 — <one line>

## Notes for a fresh session
<anything decided in chat that a new session must know>
''', encoding="utf-8")
print("OK references/status-template.md")

# ---------- 3. scripts/factory.sh ----------
p = R / "scripts" / "factory.sh"
t = p.read_text(encoding="utf-8")

old_fs = '''      if [ -f "$d/00-status.md" ] &&
         grep -Eq '^- Gate 4 — Slice plan: APPROVED([[:space:]]|$)' "$d/00-status.md"; then
        [ -f "$d/04-slices.md" ] || {
          red "    MISSING 04-slices.md (Gate 4 is approved)"
          fail=1
        }
      fi'''

new_fs = old_fs + '''
      if [ -f "$d/00-status.md" ] &&
         grep -Eq '^- Gate [1-4] — [^:]+: INVALIDATED' "$d/00-status.md" 2>/dev/null; then
        yellow "    gate INVALIDATED — re-approve before continuing"
      fi'''

t = replace_once(t, old_fs, new_fs, "factory.audit")
p.write_text(t, encoding="utf-8")
print("OK scripts/factory.sh")

# ---------- 4. SKILL.md ----------
p = R / "SKILL.md"
t = p.read_text(encoding="utf-8")

old_sk = '''Do not narrate what you are about to do. Do the work in the response: ask the
questions, draft the doc, present the summary. A numbered plan of what you will
do is a failure.

1. Write the gate doc to disk.
2. Present at most 5-10 bullet decisions plus the doc path. Do not paste the whole doc.
3. Ask exactly: "Approve Gate N, or what should change?"
4. Approval = the user clearly says yes / approve / continue. Anything else:
   revise the doc, re-ask.
5. On approval: mark the gate APPROVED in `00-status.md`, move on.
6. **Stop after the ask.** Do not plan past the current gate. Do not describe what Gate N+1 will do.
7. **Backtracking:** if a later gate reveals an earlier decision is wrong, stop,
   update the earlier doc, set that gate back to "in progress", re-approval before continuing.'''

new_sk = '''**Before you begin:** Do not narrate what you are about to do. Do the work in
the response: ask the questions, draft the doc, present the summary. A numbered
plan of what you will do is a failure. **Stop after the ask** — do not plan past
the current gate or describe what Gate N+1 will do.

1. Write the gate doc to disk.
2. Present at most 5-10 bullet decisions plus the doc path. Do not paste the whole doc.
3. Ask exactly: "Approve Gate N, or what should change?"
4. Approval = the user clearly says yes / approve / continue. Anything else:
   revise the doc, re-ask.
5. On approval: edit the gate's line in `00-status.md` to
   `APPROVED <YYYY-MM-DD>`, move on.

### Backtracking (only when a later gate invalidates an earlier one)

1. Stop. Do not continue the later gate.
2. In `00-status.md`, change the earlier gate's line to
   `INVALIDATED <YYYY-MM-DD> by gate-N`. Do not delete the old approval.
3. Update the earlier doc; set that gate's line to `in progress`.
4. Ask the user to re-approve the earlier gate (same protocol above).
5. The later gate's draft is frozen, not carried forward: resume it only after
   the earlier gate is re-approved.'''

t = replace_once(t, old_sk, new_sk, "skill.approval")
p.write_text(t, encoding="utf-8")
print("OK SKILL.md")

print("\\nAll four files updated. Run: scripts/factory.sh audit && scripts/factory.sh check-skill")
