# Architecture: --answer-file flag

## Fit
Touches harness.py, which handles CLI args and input flow. No other services/modules are impacted.

## Endpoints
none

## Data
none (no tables/collections; only local Python variables and the existing messages list change)

## Flow
1. Parse sys.argv for --answer-file <path>
2. If present: read file once at startup
3. Replace input() calls with file contents
4. If absent: fallback to standard input()

## External
none (uses existing Ollama endpoint at http://localhost:11434/api/chat, no new services)