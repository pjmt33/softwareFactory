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

def call(messages):
    p = {"model": M, "messages": messages, "stream": False, "think": True, "tools": TOOLS}
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
    messages = [{"role": "user", "content":
        f"You are executing a gate.\n\nGATE REFERENCE:\n{rf(gate_ref)}\n\nSTATUS:\n{rf(status)}\n\nTASK:\n{task}\n\n"
        "Tools: read_file, write_file. RULE: you MUST ask your clarifying questions BEFORE calling write_file. "
        "Do not re-read a file you already read. After two turns, if you have not asked or written, you will be told to stop and ask."}]
    read_cache = set()
    asked = False
    stall = 0
    for turn in range(15):
        print(f"\n--- Turn {turn+1} ---", file=sys.stderr)
        msg = call(messages).get("message", {})
        if msg.get("thinking"):
            print(f"[thinking] {msg['thinking'][:160]}...", file=sys.stderr)
        tcs = msg.get("tool_calls") or []
        if not tcs:
            content = msg.get("content", "").strip()
            if any(w in content.lower() for w in ["approved", "protocol complete", "completes the gate"]):
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content":
                    "You cannot approve the gate; approval is human. State the draft is ready and ask the clarifying questions."})
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
                    stall = 0
                    continue
            return content
        messages.append(msg)
        for tc in tcs:
            fn = tc.get("function", {})
            name, args = fn.get("name"), fn.get("arguments", {})
            if name == "write_file" and not asked:
                result = "REJECTED: ask clarifying questions before writing. Ask them now."
            elif name == "read_file":
                p = args.get("path", "")
                if p in read_cache:
                    result = f"Already read {p}. Do not re-read. Ask your clarifying questions now."
                else:
                    result = rf(p)
                    read_cache.add(p)
            elif name == "write_file":
                result = wf(args.get("path", ""), args.get("content", ""))
            else:
                result = f"Unknown tool: {name}"
            print(f"[tool] {name} -> {str(result)[:80]}...", file=sys.stderr)
            messages.append({"role": "tool", "tool_name": name, "content": result})
        stall += 1
        if stall >= 2 and not asked:
            messages.append({"role": "user", "content":
                "STOP reading. You have all the context. Ask your three clarifying questions now, in one message."})
            stall = 0
    return "ERROR: max turns exceeded"

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: harness.py <gate_ref> <status> <task>"); sys.exit(1)
    print("\n=== FINAL OUTPUT ===\n" + run(sys.argv[1], sys.argv[2], sys.argv[3]))
