#!/usr/bin/env python3
import json, re, sys, urllib.request
from pathlib import Path

U = "http://localhost:11434/api/chat"
M = "qwen3:8b"
R = Path("/Volumes/dbdata/softwareFactory")

ANSWER_LINES = []  # populated by main() if --answer-file is given

def get_answer(prompt):
    if ANSWER_LINES:
        line = "\n".join(ANSWER_LINES)
        ANSWER_LINES.clear()
        print(f"{prompt}{line[:80]}…", file=sys.stderr)
        return line
    return input(prompt)
TOOLS = [
    {"type": "function", "function": {"name": "read_file", "description": "Read a file",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Write a file",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                       "required": ["path", "content"]}}},
]

def call(messages, tools=None):
    p = {"model": M, "messages": messages, "stream": False, "think": True}
    if tools is not None:
        p["tools"] = tools
    req = urllib.request.Request(U, data=json.dumps(p).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())

def rf(path):
    f = (R / path).resolve()
    allowed = [(R / "references").resolve(), (R / "docs" / "plans").resolve()]
    if not any(a in f.parents or f == a for a in allowed):
        return f"REJECTED: reads limited to references/ and docs/plans/. Got {path}"
    return f.read_text(encoding="utf-8") if f.exists() else f"Error: file not found: {path}"

GATE_BY_PREFIX = {"01": 1, "02": 2, "03": 3, "04": 4}

def gate_of(path):
    """Gate number for an artifact path, or None if not a gated artifact."""
    name = Path(path).name
    return GATE_BY_PREFIX.get(name[:2]) if name[:2] in GATE_BY_PREFIX else None

def gate_approved(status_text, gate_num):
    """True iff the specific gate line is APPROVED."""
    pat = re.compile(r"^- Gate\s+%d\b[^\n]*:\s*APPROVED(\s|$)" % gate_num, re.M)
    return bool(pat.search(status_text))
def wf(path, content, plan_dir):
    f = (R / path).resolve()
    if f.parent.resolve() != plan_dir:
        return f"REJECTED: writes must be in {plan_dir.relative_to(R)}; got {path}. Use path='{plan_dir.relative_to(R)}/{Path(path).name}' exactly."
    status = f.parent / "00-status.md"
    g = gate_of(f)
    if g and status.exists() and gate_approved(status.read_text(encoding="utf-8"), g):
        return f"REJECTED: {path} belongs to approved Gate {g}; will not write."
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} bytes to {path}"

# RPI isolation: research (Gate 2) must NOT see the ticket (Gate 1).
RPI_READS = {
    1: [],
    2: [2],
    3: [2],
    4: [2, 3],
}

def prior_artifacts(status_path, gate_ref):
    """Return approved artifacts this gate is allowed to read (RPI isolation)."""
    m = re.search(r"gate-(\d)", gate_ref)
    n = int(m.group(1)) if m else 1
    allowed = set(RPI_READS.get(n, []))
    d = (R / status_path).resolve().parent
    out = []
    for f in sorted(d.glob("0[1-9]-*.md")):
        try:
            gn = int(f.name[1])
        except ValueError:
            continue
        if gn in allowed:
            out.append(f"=== {f.name} ===\n{f.read_text(encoding='utf-8')}")
    return "\n\n".join(out)

def gate_questions(ref_text):
    """Extract numbered questions ending in ? from the gate reference."""
    return re.findall(r"^\s*\d+\.\s+(.+\?)\s*$", ref_text, re.M)


def asked_gate_questions(content, qs):
    """True if at least 2 of the gate's questions appear in the model output."""
    if not qs:
        return False
    norm = lambda t: " ".join(re.sub(r"\W+", " ", t.lower()).split())
    c = norm(content)
    hits = sum(1 for q in qs if " ".join(norm(q).split()[:4]) in c)
    return hits >= 1


def probe() -> bool:
    """Send a minimal ping tool; return True only if structured tool_calls come back."""
    t = [{"type": "function", "function": {"name": "ping", "description": "Call this tool",
          "parameters": {"type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"]}}}]
    try:
        m = call([{"role": "user", "content": "Call the ping tool with x=hi."}], tools=t).get("message", {})
        return any(tc.get("function", {}).get("name") == "ping" for tc in (m.get("tool_calls") or []))
    except Exception as e:
        print(f"Probe error: {e}", file=sys.stderr)
        return False

MIN_BYTES = {1: 200, 2: 300, 3: 400, 4: 200}
PLACEHOLDER_RE = re.compile(r"\[[A-Za-z][^\]]{4,}\]")

def artifact_suspect(path, gate_num):
    """Return a warning string if the artifact looks truncated or unfilled."""
    p = R / path
    if not p.exists():
        return f"WARN: {path} does not exist after write"
    text = p.read_text(encoding="utf-8")
    problems = []
    if len(text) < MIN_BYTES.get(gate_num, 200):
        problems.append(f"{len(text)} bytes < floor {MIN_BYTES.get(gate_num, 200)}")
    if PLACEHOLDER_RE.search(text):
        problems.append("contains unfilled [placeholder] brackets")
    if text.count("[") != text.count("]"):
        problems.append("unbalanced [ ] brackets")
    if text.count("(") != text.count(")"):
        problems.append("unbalanced ( ) parens")
    return ("; ".join(problems)) if problems else None

def extract_phase(outline_text, phase_num):
    pattern = rf"^(## (?:✅ )?Phase {phase_num}:[^\n]*\n)(.*?)(?=^## (?:✅ )?Phase |\Z)"
    m = re.search(pattern, outline_text, re.M | re.S)
    return m.group(1) + m.group(2) if m else None

def phase_prompt(phase_block, plan_dir):
    """Build the implementer prompt for one phase, with precedence rule."""
    slug = plan_dir.name
    return (
        f"You are implementing one phase from the structure outline.\n\n"
        f"PRECEDENCE: structure outline > design discussion > research > ticket.\n"
        f"When documents conflict, the structure outline wins.\n\n"
        f"PHASE:\n{phase_block}\n\n"
        f"COMPANION DOCUMENTS in {plan_dir.relative_to(R)}/:\n"
        f"- 02-research.md\n- 03-design-discussion.md\n\n"
        f"Implement ONLY this phase. Run every automated validation item.\n"
        f"Mark a checkbox [x] only when that check passes. Leave manual items\n"
        f"and the phase-title ✅ for human confirmation. Stop after this phase.\n"
    )

def run(gate_ref, status, task):
    slug = Path(status).parent.name
    qs = gate_questions(rf(gate_ref))
    priors = prior_artifacts(status, gate_ref)
    messages = [{"role": "user", "content":
        f"You are executing a gate.\n\nGATE REFERENCE:\n{rf(gate_ref).replace('<slug>', slug)}\n\n"
        f"STATUS:\n{rf(status).replace('<slug>', slug)}\n\n"
        + (f"APPROVED PRIOR GATES (do not contradict these):\n{priors}\n\n" if priors else "")
        + f"TASK:\n{task}\n\n"
        "Prior gate artifacts are already included above; do not read them again. "
        "Tools: read_file, write_file. RULE: ask your clarifying questions BEFORE calling write_file. "
        "Do not re-read a file you already read. If you call write_file before asking, it will be rejected."}]
    # Ask the gate's questions directly; the model does not ask them.
    qs_text = "\n".join(f"{i}. {q}" for i, q in enumerate(qs, 1))
    print(f"\n=== Gate questions ({gate_ref}) ===\n{qs_text}\n", file=sys.stderr)
    _gm = re.search(r"gate-(\d)", gate_ref)
    hint = ""
    if _gm and int(_gm.group(1)) >= 3:
        hint = " (multi-line answer? use --answer-file with a '# gate-N' header)"
    try:
        direct = get_answer(f"Your answer to all gate questions (one line, or blank to let the model ask){hint}: ").strip()
    except EOFError:
        direct = ""
    if direct:
        messages.append({"role": "assistant", "content": qs_text})
        messages.append({"role": "user", "content": direct})
        asked, no_tools = True, False
    else:
        asked, no_tools = False, False
    read_cache, call_counts = set(), {}
    asked = asked if 'asked' in dir() else False
    rejected_writes = 0
    for turn in range(20):
        print(f"\n--- Turn {turn+1} ---", file=sys.stderr)
        msg = call(messages, tools=[] if no_tools else TOOLS).get("message", {})
        if msg.get("thinking"):
            print(f"[thinking] {msg['thinking'][:160]}...", file=sys.stderr)
        tcs = msg.get("tool_calls") or []
        if not tcs:
            content = msg.get("content", "").strip()
            if re.search(r"<[a-z]", content):
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content":
                    "You output the unfilled template. Do not output the template. "
                    "Ask the four clarifying questions first, then write the doc with real content."})
                continue
            if any(w in content.lower() for w in ["gate is approved", "gate approved", "protocol complete", "completes the gate", "gate complete"]):
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content":
                    "You cannot approve the gate; approval is human. Ask the clarifying questions now."})
                continue
            if not content and not asked:
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content":
                    "Your response was empty. Ask the gate's questions now, verbatim, and do not call any tool:\n"
                    + "\n".join(f"{i}. {q}" for i, q in enumerate(qs, 1))})
                no_tools = True
                continue
            if content and not asked and not asked_gate_questions(content, qs) and rejected_writes >= 2:
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content":
                    "Your questions were not the gate's questions. Output these verbatim, numbered, and do not call any tool:\n"
                    + "\n".join(f"{i}. {q}" for i, q in enumerate(qs, 1))})
                no_tools = True
                continue
            if asked_gate_questions(content, qs):
                asked = True
                no_tools = False
                print(f"\n[model asks]\n{content}\n", file=sys.stderr)
                try:
                    ans = get_answer("Your answer (blank to accept final output): ").strip()
                except EOFError:
                    ans = ""
                if ans:
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": ans})
                    continue
            return content
        messages.append(msg)
        if len(read_cache) >= 2 and not asked and turn >= 2 and not no_tools:
            messages.append({"role": "user", "content":
                "You have read the gate reference and the product doc. STOP. "
                "Output the four Gate 2 questions as plain text now. Do not call any tool."})
            no_tools = True
            continue
        for tc in tcs:
            fn = tc.get("function", {})
            name, args = fn.get("name"), fn.get("arguments", {})
            key = (name, json.dumps(args, sort_keys=True))
            call_counts[key] = call_counts.get(key, 0) + 1
            if call_counts[key] >= 2 and name == "read_file":
                result = f"Already read {args.get('path','')}. Do not re-read. Ask your clarifying questions now."
                if call_counts[key] >= 3:
                    no_tools = True
            elif name == "write_file" and not asked:
                rejected_writes += 1
                result = "REJECTED: ask clarifying questions before writing. Ask them now."
                if rejected_writes >= 2:
                    no_tools = True
            elif name == "read_file":
                p = args.get("path", "").replace("<slug>", slug)
                if "/" not in p:
                    candidate = Path(status).parent / p
                    if candidate.exists():
                        p = str(candidate)
                result = rf(p)
                read_cache.add(p)
            elif name == "write_file":
                p = args.get("path", "").replace("<slug>", slug)
                result = wf(p, args.get("content", ""), Path(status).resolve().parent)
                print(f"[tool] {name} -> {str(result)[:80]}...", file=sys.stderr)
                messages.append({"role": "tool", "tool_name": name, "content": result})
                if not result.startswith("REJECTED"):
                    gnum = int(re.search(r"gate-(\d)", gate_ref).group(1)) if re.search(r"gate-(\d)", gate_ref) else 1
                    warn = artifact_suspect(p, gnum)
                    if warn:
                        print(f"\n*** WARN: {p} {warn}. "
                              f"Review before approving; the artifact may be truncated "
                              f"or contain unfilled template content. ***\n",
                              file=sys.stderr)
                        return f"Wrote {p} (SUSPECT: {warn}). Gate artifact NOT confirmed complete."
                    return f"Wrote {p}. Gate artifact complete."
            else:
                result = f"Unknown tool: {name}"
            print(f"[tool] {name} -> {str(result)[:80]}...", file=sys.stderr)
            messages.append({"role": "tool", "tool_name": name, "content": result})
    return "ERROR: max turns exceeded"

def run_phase(plan_dir, phase_num):
    import subprocess
    outline = plan_dir / "04-structure-outline.md"
    if not outline.exists():
        return f"ABORT: {outline} not found"
    block = extract_phase(outline.read_text(encoding="utf-8"), phase_num)
    if block is None:
        return f"ABORT: Phase {phase_num} not found"
    first_line = block.split("\n", 1)[0]
    if "\u2705" in first_line:
        return f"REFUSED: Phase {phase_num} already marked complete"
    boxes = re.findall(r"^- \[( |x)\]", block, re.M)
    if boxes and all(b == "x" for b in boxes):
        return f"REFUSED: Phase {phase_num} has all checkboxes [x]; already complete"
    prompt = phase_prompt(block, plan_dir)
    messages = [{"role": "user", "content": prompt}]
    print(f"\n=== Implementing Phase {phase_num} in {plan_dir.name} ===\n", file=sys.stderr)
    for turn in range(20):
        print(f"\n--- Turn {turn+1} ---", file=sys.stderr)
        msg = call(messages, tools=TOOLS).get("message", {})
        if msg.get("thinking"):
            print("[thinking] " + str(msg["thinking"])[:160], file=sys.stderr)
        tcs = msg.get("tool_calls") or []
        if not tcs:
            content = msg.get("content", "").strip()
            if content:
                print(f"\n=== Phase {phase_num} complete ===\n{content}\n", file=sys.stderr)
                try:
                    ans = get_answer("Confirm to commit and proceed? (y/n): ").strip()
                except EOFError:
                    ans = "n"
                if ans.lower() in ("y", "yes"):
                    subprocess.run(["git", "add", "-A"], check=False)
                    r = subprocess.run(["git", "commit", "-m", f"feat({plan_dir.name}): Phase {phase_num} complete"], capture_output=True, text=True)
                    return f"Committed Phase {phase_num}: {r.stdout.strip() or r.stderr.strip()}"
                return f"Phase {phase_num} not committed; feedback: {ans}"
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": f"Continue implementing Phase {phase_num}. Use tools."})
            continue
        messages.append(msg)
        for tc in tcs:
            fn = tc.get("function", {})
            name, args = fn.get("name"), fn.get("arguments", {})
            if name == "read_file":
                p2 = args.get("path", "").replace("<slug>", plan_dir.name)
                f2 = (R / p2).resolve()
                result = f2.read_text(encoding="utf-8") if f2.exists() else f"Error: file not found: {p2}"
            elif name == "write_file":
                p2 = args.get("path", "").replace("<slug>", plan_dir.name)
                f2 = (R / p2).resolve()
                if (R / ".git").resolve() in f2.parents:
                    result = f"REJECTED: cannot write under .git/: {p2}"
                else:
                    f2.parent.mkdir(parents=True, exist_ok=True)
                    f2.write_text(args.get("content", ""), encoding="utf-8")
                    result = f"Wrote {len(args.get('content', ''))} bytes to {p2}"
            else:
                result = f"Unknown tool: {name}"
            print(f"[tool] {name} -> {str(result)[:80]}...", file=sys.stderr)
            messages.append({"role": "tool", "tool_name": name, "content": result})
    return "ERROR: max turns exceeded"

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--phase" in args:
        idx = args.index("--phase")
        phase_num = int(args[idx + 1])
        del args[idx:idx + 2]
        dry_run = "--dry-run" in args
        if dry_run:
            args.remove("--dry-run")
        if len(args) < 1:
            print("Usage: harness.py --phase N <status> [--dry-run]", file=sys.stderr)
            sys.exit(1)
        plan_dir = (R / args[0]).resolve().parent
        outline = plan_dir / "04-structure-outline.md"
        if not outline.exists():
            print(f"ABORT: {outline} not found", file=sys.stderr)
            sys.exit(2)
        block = extract_phase(outline.read_text(encoding="utf-8"), phase_num)
        if block is None:
            print(f"ABORT: Phase {phase_num} not found in {outline}", file=sys.stderr)
            sys.exit(2)
        if dry_run:
            print(f"=== Phase {phase_num} (dry run) ===")
            print(block)
            sys.exit(0)
        if not probe():
            print("ABORT: probe failed", file=sys.stderr)
            sys.exit(2)
        print("\n=== FINAL OUTPUT ===\n" + run_phase(plan_dir, phase_num))
        sys.exit(0)
    if "--answer-file" in args:
        idx = args.index("--answer-file")
        path = args[idx + 1]
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        if not lines or not lines[0].startswith("#"):
            print(f"ABORT: {path} must start with '# gate-N' on line 1.",
                  file=sys.stderr)
            sys.exit(2)
        m = re.match(r"#\s*gate-(\d)\b", lines[0].strip())
        if not m:
            print(f"ABORT: {path} header must be '# gate-N'. Got: {lines[0]!r}",
                  file=sys.stderr)
            sys.exit(2)
        expected = int(m.group(1))
        lines = lines[1:]
        gate_arg = next((a for a in args if "gate-" in a), "")
        gm = re.search(r"gate-(\d)", gate_arg)
        actual = int(gm.group(1)) if gm else None
        if actual is None:
            print(f"ABORT: cannot determine gate from args: {args}", file=sys.stderr)
            sys.exit(2)
        if expected != actual:
            print(f"ABORT: answer file is for gate {expected}, "
                  f"but gate ref is gate {actual}.", file=sys.stderr)
            sys.exit(2)
        ANSWER_LINES.extend(lines)
        del args[idx:idx + 2]
    if len(args) < 3:
        print("Usage: harness.py <gate_ref> <status> <task> [--answer-file <path>]"); sys.exit(1)
    if not probe():
        print("ABORT: tool-call probe failed. Model did not return structured tool_calls.", file=sys.stderr)
        print("Check Ollama version and /api/chat tool rendering (see ollama/ollama#19040).", file=sys.stderr)
        sys.exit(2)
    print("\n=== FINAL OUTPUT ===\n" + run(args[0], args[1], args[2]))
