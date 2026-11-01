## Phase 1: read-only inventory page
Files: scripts/webui.py (new, stdlib http.server), scripts/factory.sh (read-only — not modified)
Validation: `python3 scripts/webui.py --port 8765 & sleep 1; N=$(curl -s http://localhost:8765/ | grep -c 'all gates approved'); M=$(curl -s http://localhost:8765/ | grep -c 'next ->'); pkill -f "webui.py --port 8765"; test "$N" = "6" -a "$M" = "1"`
- [x] server starts
- [x] page lists every plan
- [x] fully-approved plans show "all gates approved"

## Phase 2: phase checkboxes in the page
Files: scripts/webui.py
Validation: `curl -s http://localhost:8765/ | grep -c 'Phase 1:'` returns ≥ 1
- [ ] phase headers show
- [ ] checked boxes render
