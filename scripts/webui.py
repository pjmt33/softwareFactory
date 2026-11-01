# ─── IMPORTS ──────────────────────────────────────────────────────────────────
# http.server: the stdlib HTTP server. No Flask, no dependency.
# socketserver: the TCP server that wraps http.server.
# os: not currently used; kept for parity with the earlier draft. Safe to remove.
# re: the gate-line and checkbox-line regexes.
# pathlib.Path: resolve R and walk docs/plans/.
import http.server
import socketserver
import os
import re
from pathlib import Path

# ─── CONFIG ───────────────────────────────────────────────────────────────────
# R = repo root. `__file__` is scripts/webui.py, so `.parent` is scripts/,
# `.parent.parent` is the repo root. Every path below is relative to R.
R = Path(__file__).resolve().parent.parent
# PORT: 8765. The Phase 1 validation hardcodes this port; changing it means
# changing the Validation line in 04-structure-outline.md too.
PORT = 8765


# ─── INVENTORY ────────────────────────────────────────────────────────────────
def inventory():
    """Walk docs/plans/*/00-status.md and 04-structure-outline.md, return HTML."""
    # rows: the HTML <li> strings, in order. Plans first, then their phases.
    rows = []
    plans_dir = R / "docs" / "plans"
    # If docs/plans/ doesn't exist, return an empty list. The page still serves.
    if not plans_dir.exists():
        return "<ul></ul>"

    # Iterate plan dirs sorted by name. `_smoke-test` is skipped by the `_`
    # prefix check — it's an intentional artifact, not a real plan.
    for d in sorted(plans_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        status = d / "00-status.md"
        # A plan dir without a status file isn't a plan. Skip it.
        if not status.exists():
            continue

        # Parse the gate lines. Format from references/status-template.md:
        #   - Gate N — Label: STATE
        # STATE is "pending", "in progress", "APPROVED <date>", or
        # "INVALIDATED <date> by gate-N".
        lines = status.read_text(encoding="utf-8").splitlines()
        gates = []
        for ln in lines:
            m = re.match(r"^- Gate ([1-4]) — ([^:]+): (.+)$", ln)
            if m:
                gates.append((int(m.group(1)), m.group(2), m.group(3).strip()))
        # No gate lines? Not a plan. Skip.
        if not gates:
            continue

        # The first gate whose state does NOT start with "APPROVED" is the
        # open gate. `INVALIDATED` and `in progress` and `pending` all count
        # as open; only `APPROVED <date>` is done.
        open_gate = next((g for g in gates if not g[2].startswith("APPROVED")), None)

        # Render the plan's row. `next ->` is emitted UNESCAPED (`->`, not
        # `-&gt;`) so `grep -c 'next ->'` matches in the validation.
        # This was the Phase 1 bug: the HTML entity broke the grep.
        if open_gate:
            rows.append(f"<li>{d.name}: next -> Gate {open_gate[0]} ({open_gate[1]})</li>")
        else:
            rows.append(f"<li>{d.name}: all gates approved</li>")

        # ─── PHASE 2: phase headers and checkboxes ─────────────────────────
        # Read 04-structure-outline.md and render each `## Phase N:` header
        # and each `- [ ]` / `- [x]` checkbox. Indented for visual nesting:
        # headers at 2em, checkboxes at 3em.
        outline = d / "04-structure-outline.md"
        if outline.exists():
            for ln in outline.read_text(encoding="utf-8").splitlines():
                if ln.startswith("## Phase ") or ln.startswith("## ✅ Phase "):
                    rows.append(f"<li style='margin-left:2em'>{ln}</li>")
                elif re.match(r"^- \[[ x]\]", ln):
                    rows.append(f"<li style='margin-left:3em'>{ln}</li>")

    # Empty result → a single placeholder row. The page still serves, and
    # `grep -c 'all gates approved'` returns 0 — which is a real signal.
    if not rows:
        return "<ul><li>(no plans)</li></ul>"
    return "<ul>\n" + "\n".join(rows) + "\n</ul>"


# ─── HTTP HANDLER ─────────────────────────────────────────────────────────────
class H(http.server.BaseHTTPRequestHandler):
    """One route: GET / returns the inventory page."""

    def do_GET(self):
        # The page is a single string. `<meta charset='utf-8'>` so the ✅
        # in phase headers renders instead of throwing UnicodeEncodeError.
        body = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Software Factory</title>"
            # Minimal styling: monospace, indented list items. No CSS file.
            "<style>body{font-family:monospace;margin:2em}"
            "li{margin:0.2em 0}</style></head><body>"
            "<h1>Software Factory</h1>"
            f"{inventory()}"
            "</body></html>"
        )
        # 200, HTML, explicit utf-8. The body is bytes, not str.
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, fmt, *args):
        # Silence per-request logging. Without this, every `curl` in the
        # validation prints `127.0.0.1 - - [...] "GET / ..." 200 -` to
        # stderr, which pollutes the `[verify]` output.
        pass


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # TCPServer on PORT, handler H. serve_forever() blocks.
    # Ctrl-C raises KeyboardInterrupt; the `with` closes the socket.
    # `pkill -f "webui.py --port 8765"` in the validation kills it cleanly.
    with socketserver.TCPServer(("", PORT), H) as httpd:
        print(f"http://localhost:{PORT}/")
        httpd.serve_forever()
