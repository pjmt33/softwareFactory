# Product: audit visibility

## Problem
Operators resuming a feature need to see which approved plans still have unchecked slices, so they know what work remains without opening every 04-slices.md by hand.

## Success metric
Every plan directory with at least one unchecked slice appears in one audit run, and plans with all slices checked do not.

## Announcement — the blog post before the feature
Run factory.sh audit and see exactly which slices remain unchecked across all plans. No more grepping 04-slices.md by hand, no more guessing what is left. The audit now tells you what to do next.

## Screens
no UI, terminal output only