---
name: grill-me-for-pr
description: Pre-PR readiness check — cleanup, refactoring, and reviewer-friction analysis before opening a PR.
argument-hint: "[target branch or review focus]"
---

Run a **Pre-PR Readiness** review on the current branch using `@reviewer`.

## Instructions

1. Determine the target branch (default: `main`). If unclear, ask once.
2. Switch to **Pre-PR Readiness Mode** (see reviewer agent).
3. Diff the current branch against target, analyze all changes, and produce the full readiness report.
4. End with a prioritized action-item checklist I can work through.

Be harsh — I'd rather fix things now than get rejected in review.
