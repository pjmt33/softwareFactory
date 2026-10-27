# Product: resume-next-gate

## Problem
User needs resume to say which gate is next for every plan, so a fresh session does not have to read four status lines and guess.

## Success metric
100% of plans with unapproved gates print the next gate as "<slug>: next -> Gate N (Label)" in terminal output, measured by checking the output of the resume command.

## Announcement — the blog post before the feature
Run factory.sh resume and it tells you exactly which gate to work on next for every plan in the repo. No more reading status files to figure out what is left.

## Screens
no UI