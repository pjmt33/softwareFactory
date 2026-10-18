# Software Factory Local Agent

A local agent that fixes Ollama's streaming tool-drop bug by calling
`/api/chat` with `stream: false` when tools are present. Exposes an
OpenAI-compatible `/v1/chat/completions` endpoint so Poseidon (or any
OpenAI client) can talk to it.

## Run

    pip install -r requirements.txt
    python agent.py

## Point Poseidon at it

    Base URL: http://localhost:8082/v1
    Model:    qwen2.5:latest

Pass a stable `conversation_id` in each request (or the `X-Conversation-ID`
header) so session logs and gate context remain associated. The bridge also
returns the selected conversation ID in each completion. When the client omits
one, a stable ID is derived from its `user` field and first user message.

Before connecting Poseidon, verify that port 8082 is free and that the listener
is the agent process. The root endpoint is `/`, the bridge health endpoint is
`/health`, and the OpenAI-compatible model list is `/v1/models`.

## What gets stored

    data/ledger/runs.jsonl        every event, append-only
    data/ledger/writes.jsonl      every file write, with prior content
    data/sessions/<id>/           full conversation per session
    data/sessions/<id>/state.json active plan slug for gate enforcement
    data/incidents/incidents.md   agent corrections and lessons, append-only
    logs/agent.log                debug log

Event ledgers and conversation logs are append-only; the small session state
file is updated when the active plan changes. If a run goes wrong, inspect
`data/sessions/<id>/` for the messages, tool calls, and errors.
For request arrival, inspect `logs/agent.log`; for agent actions, inspect
`data/ledger/runs.jsonl`; for model messages, inspect the session's
`messages.jsonl`.
