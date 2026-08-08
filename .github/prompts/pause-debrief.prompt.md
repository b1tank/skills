---
name: pause-debrief
description: Pause for a concise progress debrief, reconcile plans and docs, and surface forward blockers with recommendations.
---

Pause implementation and give a candid mid-course debrief before more investment.

1. Read the repository instructions, current plans/specs/roadmap, status, relevant implementation, and tests. Verify important claims from code or focused checks instead of trusting checked boxes or prior summaries.
2. Summarize:
   - what is complete and actually verified;
   - what remains in the current milestone;
   - the next acceptance gate;
   - blockers or assumptions beyond current progress that could change the path.
3. For each material blocker, use your own judgment to classify it as:
   - resolve autonomously before continuing;
   - needs a user decision now; or
   - documented later limitation.
   Give concise evidence, impact, recommendation, and smallest safe resolution or experiment. Do not inflate ordinary follow-up work into a blocker or re-list known limitations that do not affect the path ahead.
4. Ask only decisions that genuinely require user judgment. For each question, include your recommendation and safe default. Do not ask for facts you can inspect, repeat answered questions, request broad preference surveys, or end with “anything else?”
5. Reconcile project bookkeeping without changing production behavior:
   - update the canonical plan, status, roadmap, decision, or test-scope documents with verified progress, blockers, decisions needed, and the next gate;
   - mark completed work accurately;
   - remove or consolidate superseded plans and stale status documents after checking references and preserving useful history in Git;
   - correct stale instructions that contradict the current stage.
   Do not create duplicate tracking documents merely to record the debrief.
6. End with a clear go/no-go recommendation and the exact work that a subsequent `continue` would authorize.

If there are no material blockers or required decisions, say so directly and recommend continuing; do not invent questions. Do not implement the next milestone, commit, push, publish, or perform irreversible actions during the debrief unless separately authorized.

Treat a subsequent `continue` as approval of the documented recommendations and safe defaults unless the user supplied different decisions. If the user provides input, first reconcile the canonical plan/decisions with that input, then proceed from the updated next task.
