# ADR 0001: Thin harness replaces Aider and the Flask agent

Date: 2026-10-19
Status: Accepted

## Context

The software-factory workflow enforces four gates with human approval. The
original execution path used Aider with qwen2.5-coder:3b, then a Poseidon UI
with qwen2.5-coder:7b via Ollama's /v1 endpoint. Both failed: the /v1 layer
stuffed tool calls into `content` instead of `tool_calls`, and the 3B model
could not drive multi-turn gate questions. The archived Flask agent had tests
(test_agent.py) but no gate integration.

A working alternative was demonstrated: a ~150-line Python harness calling
Ollama's native /api/chat with qwen3:8b, enforcing ask-before-write, blocking
repeated reads, rejecting unfilled templates and false approvals, sandboxing
reads/writes to references/ and docs/plans/, and probing tool-call capability
before each run.

## Decision Drivers

- Gate discipline must be enforceable, not hoped for from the model.
- The execution layer must be auditable and small enough to reason about.
- Approval must remain a human action; the harness must not self-approve.
- Ollama version drift can break tool rendering; the harness must detect it.

## Considered Options

1. Manual `ollama run` per gate (the original fallback). Works, but no
   enforcement, no artifact verification, and paste-truncation on long answers.
2. Poseidon UI + /v1 proxy. Failed on serialization; the proxy did not fix
   qwen2.5-coder's text-shaped tool calls.
3. Aider with qwen2.5-coder:3b. Cannot drive multi-turn gates; ask mode does
   not execute.
4. Thin harness (chosen). Native /api/chat, qwen3:8b, explicit enforcement
   rules, sandboxed file access, startup probe.

## Decision Outcome

Chosen option: **Thin harness**, because it carried Gate 3 of gate-preambles
and Gate 2 of harness-answer-file to completion with the correct sequence:
read reference → ask gate questions → human answer → write artifact. The
model did not become reliable; the harness removed its ability to fail in the
observed ways.

### Consequences

**Good:**
- Gate artifacts are produced with the correct sequence enforced structurally.
- Reads and writes are sandboxed; approved artifacts cannot be silently
  overwritten.
- The startup probe catches Ollama tool-rendering regressions before a run.

**Bad:**
- The harness is a new component the gates did not originally govern; this
  ADR and the Gate 3 reopen are the retroactive fix.
- The model can still invent content if the task string lacks a concrete
  anchor; the harness does not validate artifact content against the answers.
- The marker heuristic for gate questions is extracted from the reference,
  but if a gate reference changes its numbering format, the extraction fails.

**Neutral:**
- The harness lives in the repo root as `harness.py`, not under a package.
  It is invoked directly with `python3 harness.py`.

## Links

- gate-preambles plan: docs/plans/gate-preambles/
- harness-answer-file plan: docs/plans/harness-answer-file/
- Commit 904b3be: harness enforcement bundled into gate-preambles approval
