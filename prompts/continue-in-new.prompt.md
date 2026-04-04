---
name: continue-in-new
description: Document current state for smooth handoff to a new session
---

Prepare a session handoff so a new agent session can continue without losing context.

## What to do

1. **Assess current state**:
   - If work is **complete**: Document what was done and what's next
   - If work is **in progress**: Note what remains and any partial state

2. **Update plan/spec files** with current state:
   - Mark completed tasks with ✅
   - Mark in-progress items with 🔄 and note what remains
   - Add "Session Handoff" section at the top of plan.md

3. **Document the immediate next step** clearly:
   - What file(s) to edit
   - What function/feature to implement
   - Any decisions made but not yet coded

4. **Note any gotchas or context**:
   - Non-obvious decisions made during this session
   - Failed approaches (so they aren't re-tried)
   - Dependencies or blockers

5. **Handle commits based on state**:
   - **Completed work**: Commit with descriptive message
   - **WIP**: Either commit with `[WIP]` prefix, or leave uncommitted with clear notes

## Output format

```
## Session Handoff

**Status:** [Complete | WIP]

**Completed this session:**
- [list of done items]

**In progress (if WIP):**
- [current item] - [what remains, what's blocking]

**Next step:**
[Specific actionable instruction for the next session]

**Context:**
- [any important decisions, gotchas, or notes]

**Files changed:**
- [list of modified files]
```
