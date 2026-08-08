---
name: work-in-silo
description: Clone a repo into a hash-suffixed folder and check out a fresh user/* branch off main.
argument-hint: "[repository path or URL]"
---

Use this trigger when the user says "work in silo" for a repo/workspace.

## What to do

1) Identify the repo path or URL. If missing, ask for it.
2) Run $clone-with-hash to create a new hash-suffixed clone.
3) Ensure the new branch name is `user/<random>` (default from the skill). Base branch should be `main` unless the user requests otherwise.
4) Report the new workspace path and branch name.

## Example

"Work in silo for example-project" → clone into `~/example-project-<hash>` and checkout `user/<random>` from `origin/main`.
