# Setup Log — Software Factory

Archive date: 2026-10-17
Original event timestamps were not recorded during the session; entries are
ordered by sequence of work, not by clock time.

## Session 1 — Build

- Scaffolded `/Volumes/dbdata/softwareFactory` with `SKILL.md`, `references/gate-1..4`, `references/status-template.md`, `docs/{plans,adr,external}`, `scripts/`.
- Wrote `scripts/factory.sh` with four subcommands: `audit`, `check-skill`, `init-feature`, `resume`.
- Validated on `qwen2.5-coder:3b` via `ollama run`.

## Verified findings

- **Fabrication**: `qwen2.5-coder:3b` in `ollama run`, given a gate template and no answers, invents plausible feature content. Reproduced 3 times. Fixed by adding a four-question preamble to `references/gate-1-product.md` that forbids drafting before the user answers.
- **Narration**: same model, given a full workflow context, produces a numbered plan of what it will do instead of doing it. Reproduced 2 times. Fixed by adding "Do not narrate" to the approval protocol in `SKILL.md` plus an imperative end-of-prompt ("Begin Gate 1 NOW...").
- **Pointer chain**: same model, given `readme.md` + `SKILL.md` + `00-status.md` only, correctly names `references/gate-1-product.md` as the next file to open. Verified once, passed.

## Hypotheses (from external sources, not yet reproduced on this machine)

- Qwen models served by Ollama emit tool calls as plain text in `content` rather than structured `tool_calls`. Source: external issue trackers. Not yet independently verified here.
- `qwen2.5-coder` family specifically lacks native tool-call training. Source: external benchmark discussion. Not yet independently verified.
- `llm-tool-proxy` closes the tool-call gap. Source: package documentation. Partially confirmed: one successful `read_file MANUAL.md` through the proxy. Full gate-loop verification pending.

## Harness investigation

- Poseidon installed via `pipx`.
- Stale sessions held the old model (`hermes3`) in `~/.poseidon/sessions.db`. Fix: delete the specific session or start a fresh session. **Never `rm sessions.db` without a backup.**
- `qwen2.5-coder:3b` failed to emit executable tool calls through Poseidon directly. Cause: Ollama's Qwen template serialization, not the model. Fix: `llm-tool-proxy` on port 8787 between Poseidon and Ollama.
- `qwen2.5:latest` through `llm-tool-proxy` succeeded: model read `MANUAL.md`, summarized accurately, asked what to do next. One clean pass.

## Superseded

- Earlier advice to `rm ~/.poseidon/sessions.db` when the harness misbehaves. Superseded: back up first, prefer a fresh session or targeted row deletion.
