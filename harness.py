#!/usr/bin/env python3
import json, sys, urllib.request
from pathlib import Path

U = "http://localhost:11434/api/chat"
M = "qwen3:8b"
R = Path("/Volumes/dbdata/softwareFactory")

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
    f = R / path
    return f.read_text(encoding="utf-8") if f.exists() else f"Error: file not found: {path}"

def wf(path, content):
    f = R / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} bytes to {path}"

def run(gate_ref, status, task):
    slug = Path(status).parent.name
    messages = [{"role": "user", "content":
        f"You are executing a gate.\n\nGATE REFERENCE:\n{rf(gate_ref).replace('<slug>', slug)}\n\n"
        f"STATUS:\n{rf(status).replace('<slug>', slug)}\n\nTASK:\n{task}\n\n"
        "Tools: read_file, write_file. RULE: ask your clarifying questions BEFORE calling write_file. "
        "Do not re-read a file you already read. If you call write_file before asking, it will be rejected."}]
    read_cache, call_counts = set(), {}
    asked, rejected_writes, no_tools = False, 0, False
    for turn in range(20):
        print(f"\n--- Turn {turn+1} ---", file=sys.stderr)
        msg = call(messages, tools=[] if no_tools else TOOLS).get("message", {})
        no_tools = False
        if msg.get("thinking"):
            print(f"[thinking] {msg['thinking'][:160]}...", file=sys.stderr)
        tcs = msg.get("tool_calls") or []
        if not tcs:
            content = msg.get("content", "").strip()
            if any(w in content.lower() for w in ["approved", "protocol complete", "completes the gate"]):
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content":
                    "You cannot approve the gate; approval is human. Ask the clarifying questions now."})
                continue
            if "?" in content or "please answer" in content.lower():
                asked = True
                print(f"\n[model asks]\n{content}\n", file=sys.stderr)
                try:
                    ans = input("Your answer (blank to accept final output): ").strip()
                except EOFError:
                    ans = ""
                if ans:
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": ans})
                    continue
            return content
        messages.append(msg)
        for tc in tcs:
            fn = tc.get("function", {})
            name, args = fn.get("name"), fn.get("arguments", {})
            key = (name, json.dumps(args, sort_keys=True))
            call_counts[key] = call_counts.get(key, 0) + 1
            if call_counts[key] >= 2 and name == "read_file":
                result = f"Already read {args.get('path','')}. Do not re-read. Ask your clarifying questions now."
            elif name == "write_file" and not asked:
                rejected_writes += 1
                result = "REJECTED: ask clarifying questions before writing. Ask them now."
                if rejected_writes >= 2:
                    no_tools = True
            elif name == "read_file":
                p = args.get("path", "").replace("<slug>", slug)
                result = rf(p)
                read_cache.add(p)
            elif name == "write_file":
                p = args.get("path", "").replace("<slug>", slug)
                result = wf(p, args.get("content", ""))
            else:
                result = f"Unknown tool: {name}"
            print(f"[tool] {name} -> {str(result)[:80]}...", file=sys.stderr)
            messages.append({"role": "tool", "tool_name": name, "content": result})
    return "ERROR: max turns exceeded"

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: harness.py <gate_ref> <status> <task>"); sys.exit(1)
    print("\n=== FINAL OUTPUT ===\n" + run(sys.argv[1], sys.argv[2], sys.argv[3]))
