# Product: Resume All

## Problem
A fresh session running `scripts/factory.sh resume` sees only plans with open gates; when all plans are approved it prints "(none)", giving no overview of what exists in the repo.

## Success metric
The number of plans listed when `resume --all` is run, measured by verifying the output shows every plan directory with its status (e.g. "first-feature: all gates approved").

## Announcement — the blog post before the feature
Run `factory.sh resume --all` and see every plan in the repo, approved or open. No more guessing whether a feature exists — the resume output is the inventory.

## Screens
no UI