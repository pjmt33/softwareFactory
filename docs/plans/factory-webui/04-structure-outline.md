# Structure Outline: factory-webui

## ✅ Phase 1: read-only inventory page
Files: scripts/webui.py (new, stdlib http.server), scripts/factory.sh (read-only — not modified)
Validation: `python3 scripts/webui.py --port 8765 & sleep 1; N=$(curl -s http://localhost:8765/ | grep -c '^<li>[a-z].*: all gates approved'); P=$(curl -s http://localhost:8765/ | grep -c 'margin-left:2em'); pkill -f "webui.py --port 8765"; test "$N" -ge 1 -a "$P" -ge 1`
- [x] server starts
- [x] page lists every plan
- [x] fully-approved plans show "all gates approved"

## ✅ Phase 2: phase checkboxes in the page
Files: scripts/webui.py
Validation: `python3 scripts/webui.py --port 8765 & sleep 1; N=$(curl -s http://localhost:8765/ | grep -c 'margin-left:3em'); pkill -f "webui.py --port 8765"; test "$N" -ge 1`
- [x] phase headers show
- [x] checked boxes render
