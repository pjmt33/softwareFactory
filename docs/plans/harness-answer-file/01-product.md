# Product: --answer-file flag

## Problem
long multi-line answers pasted into harness.py's input() get truncated at the first newline, causing partial gate answers and lost work (Gate 3 lost a full run this way)

## Success metric
zero truncated answers across the next 5 gate runs, measured by comparing the answer file's line count to what the model received in the message history

## Announcement — the blog post before the feature
"harness.py now accepts --answer-file so long gate answers are read from a file instead of typed or pasted into the terminal; no more truncation at the first newline."

## Screens
no UI—CLI flag only