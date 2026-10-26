#!/usr/bin/env python3
import json, re, sys, urllib.request
from pathlib import Path

U = "http://localhost:11434/api/chat"
M = "qwen3:8b"
R = Path("/Volumes/dbdata/softwareFactory")

ANSWER_LINES = []  # populated by main() if --answer-file is given

def get_answer(prompt):
    if ANSWER_LINES:
        line = ANSWER_LINES.pop(0)
        print(f"{prompt}{line}", file=sys.stderr)
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
    return f"Wrote {len(content)} bytes to {path}"

def prior_artifacts(status_path, gate_ref):
    """Return prior approved artifacts for gates before the current one."""
    m = re.search(r"gate-(\d)", gate_ref)
    n = int(m.group(1)) if m else 1
    d = (R / status_path).resolve().parent
    out = []
    for f in sorted(d.glob("0[1-9]-*.md")):
        try:
            gn = int(f.name[1])
        except ValueError:
            continue
        if gn < n:
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
    try:
        direct = get_answer("Your answer to all gate questions (one line, or blank to let the model ask): ").strip()
    except EOFError:
        direct = ""
    if direct:
        messages.append({"role": "assistant", "content": qs_text})
        messages.append({"role": "user", "content": direct})
        asked, no_tools = True, False
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
                result = wf(p, args.get("content", ""))
                print(f"[tool] {name} -> {str(result)[:80]}...", file=sys.stderr)
                messages.append({"role": "tool", "tool_name": name, "content": result})
                if not result.startswith("REJECTED"):
                    return f"Wrote {p}. Gate artifact complete."
            else:
                result = f"Unknown tool: {name}"
            print(f"[tool] {name} -> {str(result)[:80]}...", file=sys.stderr)
            messages.append({"role": "tool", "tool_name": name, "content": result})
    return "ERROR: max turns exceeded"

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--answer-file" in args:
        idx = args.index("--answer-file")
        path = args[idx + 1]
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        expected = None
        if lines and lines[0].startswith("#"):
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
        if expected is not None and actual is not None and expected != actual:
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
