import http.server, socketserver, os, re
from pathlib import Path

R = Path(__file__).resolve().parent.parent
PORT = 8765

def inventory():
    rows = []
    for d in sorted((R / "docs" / "plans").iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        status = d / "00-status.md"
        if not status.exists():
            continue
        lines = status.read_text().splitlines()
        gates = []
        for ln in lines:
            m = re.match(r"^- Gate ([1-4]) — ([^:]+): (.+)$", ln)
            if m:
                gates.append((int(m.group(1)), m.group(2), m.group(3).strip()))
        if not gates:
            continue
        open_gate = next((g for g in gates if not g[2].startswith("APPROVED")), None)
        if open_gate:
            rows.append(f"<li>{d.name}: next -&gt; Gate {open_gate[0]} ({open_gate[1]})</li>")
        else:
            rows.append(f"<li>{d.name}: all gates approved</li>")
    return "<ul>\n" + "\n".join(rows) + "\n</ul>"

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = f"<!doctype html><html><body><h1>Software Factory</h1>{inventory()}</body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body.encode())

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), H) as httpd:
        print(f"http://localhost:{PORT}/")
        httpd.serve_forever()
