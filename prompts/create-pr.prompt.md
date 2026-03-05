---
name: create-pr
description: Create a branch (if on main) and open a PR from current diffs.
---

Create a branch and PR from the current working changes.

## Workflow

1. **Check current branch and diff state** before anything else
2. **Branch rules:**
   - On `main` → create new branch `b1tank/{descriptive-name}`, commit there
   - On a non-main branch → commit and push directly
3. **Atomic commits:** Examine the diff — if it spans multiple logical changes, split into atomic commits. Skip splitting if already atomic.
4. **Push and open PR** with a concise description capturing the core gist.
