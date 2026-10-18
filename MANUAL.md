# Software Factory Manual

This is the canonical operator guide for the repository. The workflow's
authoritative instructions are in [SKILL.md](SKILL.md) and the gate references
under [references/](references/). Historical setup and troubleshooting notes are
archived in [docs/history/setup-log.md](docs/history/setup-log.md); they are not
current instructions.

## Workflow

Use the four gates in order for substantial features:

1. **Product** — establish the user problem, success measure, announcement, and
   screens. Ask the four questions in
   [references/gate-1-product.md](references/gate-1-product.md) before drafting.
2. **Architecture** — inspect the existing code and document fit, endpoints,
   data, flow, and external dependencies in
   [references/gate-2-architecture.md](references/gate-2-architecture.md).
3. **Program Design** — specify changed files, types and signatures, call stack,
   tests, and exactly three least-confident decisions in
   [references/gate-3-program-design.md](references/gate-3-program-design.md).
4. **Vertical Slices** — document the ordered, end-to-end slices in one
   `04-slices.md` file, then implement and verify one slice at a time using
   [references/gate-4-vertical-slices.md](references/gate-4-vertical-slices.md).

At each gate, write the artifact, summarize its decisions, and stop for the
approval prompt specified in `SKILL.md`. Do not begin implementation before the
Gate 4 slice plan is approved. After each slice, verify the working result,
update the status file, and stop for the user's direction.

Trivial changes such as typos, copy edits, or a one-line config change are
exempt. Follow the complete qualification and approval rules in `SKILL.md`.

## Plan artifacts and resuming

Each feature's artifacts live in `docs/plans/<slug>/`:

- `00-status.md` — gate approvals, slice checklist, and fresh-session notes.
- `01-product.md`, `02-architecture.md`, and `03-program-design.md` — gate
  documents.
- `mockups/` — plain HTML screen mockups when the feature has a UI.
- `04-slices.md` — the approved, ordered slice plan (a single file).

Create the status file before Gate 1 from
[`references/status-template.md`](references/status-template.md). At the start
of a resumed feature, read every document in its plan directory and continue
from the first unapproved gate or unchecked slice. Do not redo an approved gate
unless the user requests it or a later gate invalidates it.

## Commands

Run from the repository root:

```sh
scripts/factory.sh audit
scripts/factory.sh check-skill
scripts/factory.sh resume
```

`audit` checks the scaffold, plan directories, approved Gate 4 slice-plan
presence, external-reference secret patterns, ADR index, skill hygiene, and git
status. A nonzero exit status indicates a failed check.

> Example only — replace `<slug>` with a lowercase feature slug; this is a usage
> form, not a literal command.

```sh
scripts/factory.sh init-feature <slug>
```

The accepted slug format is a lowercase letter followed by up to 63 lowercase
letters, digits, or hyphens. The initializer creates a new plan directory and
status file; it does not overwrite an existing plan.

## Local agent diagnostics

The local bridge listens on `127.0.0.1:8082` by default. Before connecting a
client, confirm the port is free and identify the process listening on it; do
not stop processes by broad name matching.

- Request arrival and HTTP errors: `agent/logs/agent.log`
- Agent events such as `chat_request`, `tool_read`, and `turn_end`:
  `agent/data/ledger/runs.jsonl`
- Model messages and tool activity for a conversation:
  `agent/data/sessions/<id>/messages.jsonl` and `tool_calls.jsonl`

```sh
grep 'POST /v1/chat/completions' agent/logs/agent.log
grep -E 'chat_request|tool_read|turn_end' agent/data/ledger/runs.jsonl
cat agent/data/sessions/SESSION_ID/messages.jsonl
```

Replace `SESSION_ID` with the directory name recorded in `runs.jsonl`.
Send the full conversation history on each chat-completion request and reuse a
stable `conversation_id` (or `X-Conversation-ID`) across turns. Client-supplied
system/developer messages are ignored; the bridge prepends its own policy
prompt. Planning artifacts are restricted to the active plan directory.
Implementation writes and allowlisted test/inspection commands are unavailable
until Gate 4 is approved in that plan's status file. The shell tool does not
invoke a shell and rejects commands outside its allowlist.

## Repository boundaries

- Keep this repository's skill, templates, scripts, and plan artifacts here.
- `docs/external/` is for names and references only, never secret values.
- The officeLab MCP/RAG system is referenced from `docs/external/` only; this
  repository does not configure or invoke it.
- Record durable in-repository decisions as ADRs in `docs/adr/`. If a task
  conflicts with an accepted ADR, stop and ask whether the task or ADR should
  change.

## Source of truth

For agent behavior, follow `SKILL.md` and the referenced gate documents. This
manual is an operator overview; if it conflicts with those workflow
instructions, follow the skill and gate references and update the manual.


## Execution (Intel Mac, CPU-only)

Use Aider in `ask` mode for gate discussions. It will not edit files until you switch to `code` mode.

- Model: `qwen2.5-coder:3b` (7B+ is too slow on CPU)
- Gate 1–3 discussion: `aider --model ollama_chat/qwen2.5-coder:3b --chat-mode ask`
- Gate 4 slice execution: `aider --model ollama_chat/qwen2.5-coder:3b --chat-mode code`
- Do NOT use Poseidon (retired) or the archived Flask agent.
