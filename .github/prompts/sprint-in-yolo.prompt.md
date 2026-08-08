---
name: sprint-in-yolo
description: Turn a list of tasks into a prioritized sprint and execute all of them autonomously with atomic commits.
argument-hint: "[task list or sprint goal]"
---

Execute a full sprint in YOLO mode from the task list below.

## Workflow

1. **Triage & Plan** — Summarize the tasks in prioritized order, merge similar topics, and save as `sprint.plan.md` next to the existing `plan.md` (or project root if none exists).
2. **Execute All** — Work through every task one by one. Do not ask for confirmation between tasks.
3. **Atomic Commits** — After each task, stage only the affected files and commit with a conventional commit message (`feat:`, `fix:`, `refactor:`, `docs:`). Do not batch multiple tasks into one commit.
4. **Log Hiccups** — If a task hits a blocker or requires a workaround, add a note under "Hiccups & Notes" in `sprint.plan.md` and keep moving to the next task. Never block the sprint.
5. **Build Check** — Run the project build after all tasks complete to catch regressions.
6. **Push** — Push all commits to the current branch when done.
7. **Update Plan** — Mark all tasks as done in `sprint.plan.md` with final notes.

## Rules

- **No pausing.** Move to the next task if stuck.
- **No confirmation prompts.** Use your best judgment on ambiguous items.
- **Read before editing.** Understand existing code before changing it.
- **Minimal scope.** Only change what is necessary for each task — no drive-by refactors.
- **Progressive context.** If earlier tasks inform later ones, carry that knowledge forward.

## Task List

Use the invocation input as the task list. Accept a numbered list, bullets, or a single-sentence sprint goal. If no input was supplied, use an existing project task or plan file when one clearly identifies pending work; otherwise ask for the tasks and stop.
