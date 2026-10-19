# Product: harness workflow

## Problem
the repo's README documents the retired Aider workflow and never mentions harness.py, so a new operator cannot tell how gates are actually executed.

## Success metric
a fresh operator can run Gate 1 through Gate 4 using only the README, measured by one dry-run where the README's commands are followed verbatim with no other reference.

## Announcement — the blog post before the feature
"README now documents the thin harness workflow: run harness.py with a gate reference, a status file, and a task; add --answer-file to read gate answers from a file; approval stays manual in 00-status.md."

## Screens
no UI—README only