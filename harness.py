#!/usr/bin/env python3
import json,sys,urllib.request
from pathlib import Path
U,M,R="http://localhost:11434/api/chat","qwen3:8b",Path("/Volumes/dbdata/softwareFactory")
T=[{"type":"function","function":{"name":"read_file","description":"Read a file","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},{"type":"function","function":{"name":"write_file","description":"Write a file","parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}}}]
def c(m):
 p={"model":M,"messages":m,"stream":False,"think":True,"tools":T}
 return json.loads(urllib.request.urlopen(urllib.request.Request(U,data=json.dumps(p).encode(),headers={"Content-Type":"application/json"})).read())
def rf(p):
 f=R/p
 return f.read_text(encoding="utf-8") if f.exists() else f"Error: file not found: {p}"
def wf(p,c):
 f=R/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(c,encoding="utf-8");return f"Wrote {len(c)} bytes to {p}"
def ex(n,a):
 return rf(a.get("path","")) if n=="read_file" else wf(a.get("path",""),a.get("content","")) if n=="write_file" else f"Unknown tool: {n}"
def run(g,s,t):
 m=[{"role":"user","content":f"You are executing a gate.\n\nGATE REFERENCE:\n{rf(g)}\n\nSTATUS:\n{rf(s)}\n\nTASK:\n{t}\n\nTools: read_file, write_file. When done, output final response as plain text."}]
 for i in range(15):
  print(f"\n--- Turn {i+1} ---",file=sys.stderr)
  msg=c(m).get("message",{})
  if msg.get("thinking"):print(f"[thinking] {msg['thinking'][:160]}...",file=sys.stderr)
  tc=msg.get("tool_calls") or []
  if not tc:
   ct=msg.get("content","").strip()
   if ct.endswith("?") or "Please answer" in ct:
    print(f"\n[model asks]\n{ct}\n",file=sys.stderr)
    try:a=input("Your answer (blank to accept): ").strip()
    except EOFError:a=""
    if a:m+=[{"role":"assistant","content":ct},{"role":"user","content":a}];continue
   return ct
  m.append(msg)
  for x in tc:
   fn=x.get("function",{});r=ex(fn.get("name"),fn.get("arguments",{}))
   print(f"[tool] {fn.get('name')}({list(fn.get('arguments',{}).keys())}) -> {str(r)[:80]}...",file=sys.stderr)
   m.append({"role":"tool","tool_name":fn.get("name"),"content":r})
 return "ERROR: max turns exceeded"
if __name__=="__main__":
 if len(sys.argv)<4:print("Usage: harness.py <gate_ref> <status> <task>");sys.exit(1)
 print("\n=== FINAL OUTPUT ===\n"+run(sys.argv[1],sys.argv[2],sys.argv[3]))
