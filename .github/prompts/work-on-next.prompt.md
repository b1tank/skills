---
name: work-on-next
description: Work trigger prompt for the next thing (issue/bug/feature). Routes to triage, planning, or implementation.
---

Use this as a lightweight "start working" trigger. The work can be a GitHub issue, a bug report, a feature request, or a concrete code task.

## What to do

1) **Get the work item**
- If the user provides a URL (issue/PR), fetch it.
- Otherwise ask for a short problem statement + desired outcome.

2) **Route based on intent**
- If the user wants triage (labels, repro ask, owner routing, draft response) → invoke `@triager` (if available) or handle directly.
- If the user wants a task breakdown / sequencing (especially for bigger work) → invoke `@planner`.
- If the user wants direct implementation and the scope is clearly small → proceed with implementation (or delegate to `@engineer`).

3) **Execution discipline**
- For bigger work (>100 LOC or unclear scope), invoke the `decompose-task` skill and confirm the breakdown with the user before implementing.
- Write tests for any behavioral change. Run them and show test summary before committing.
- Before any commit/PR-ready state, run the `diff-check` skill.
- If changes affect UI/UX, request human verification steps before committing.

## Output

Return:
- The next concrete action (one step)
- Any clarifying questions needed
- Optional: a short list of parallelizable follow-ups
