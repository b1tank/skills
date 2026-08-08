---
name: debug-and-fix
description: Reproduce a reported bug, trace its root cause, and propose code-level fix options before making changes.
argument-hint: "<issue or bug report>"
---

## Reported problem

Use the problem supplied with the invocation.

Investigate the reported problem, but do not edit code yet. If no problem was provided, ask the user for one and stop.

1. Read the repository instructions and inspect the worktree. Preserve unrelated changes.
2. Identify the revision where the bug was reported and the current target revision. Reproduce it on the intended merge base in an isolated worktree or equivalent clean environment.
3. Inspect recent commits and relevant issues or pull requests for overlapping fixes. Use read-only remote queries unless the user authorized external mutations.
4. Trace the complete lifecycle behind the symptom:
   - which component owns the operation and state;
   - how cancellation, replacement, and disposal work;
   - whether asynchronous cleanup is awaited;
   - which events update persistence and UI;
   - when listeners or resources are detached.
5. State the broken invariant in one sentence. Distinguish the root cause from downstream symptoms.
6. If the target revision no longer reproduces the bug, stop and identify the upstream change that fixed it. Do not propose speculative defensive code without a separate current failure mode.
7. If the bug remains, present a decision-ready report:
   - root cause with file and line references;
   - at least two viable fix options when meaningful;
   - focused code or diff snippets for each option;
   - tradeoffs, affected callers, compatibility risks, and test implications;
   - a recommended option that repairs the shared lifecycle invariant rather than one command or screen;
   - a regression-test snippet that should fail before the fix and pass afterward;
   - the focused and repository-required validation plan.
8. Ask the user which option to implement. Do not modify files until the user explicitly confirms how to proceed.

After confirmation, implement only the selected approach, rerun the original reproduction and required checks, and review the final diff for stale assumptions or symptom-only cleanup. Do not commit, push, close issues, or update pull requests unless the user explicitly requests those actions.
