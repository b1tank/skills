---
name: rank-by-priority
description: Validate and rank findings from critical to nitpick by user impact and fix priority.
---

Rank the supplied findings, tasks, review comments, documentation gaps, or risks from critical to nitpick. If the invocation has no usable input, rank the most recent concrete findings in the conversation or current review; if none exist, ask for the list and stop.

1. Read the applicable repository instructions and inspect enough source, tests, documentation, or runtime evidence to verify each item before ranking it. Preserve unrelated worktree changes and remain read-only unless the user separately asks for fixes.
2. Normalize overlapping items, split findings only when their impacts or remedies materially differ, and exclude invalid, obsolete, or duplicate findings with a concise reason.
3. Assign both:
   - **Severity:** consequence if left unfixed.
   - **Fix priority:** how soon it should be addressed, considering reachability, frequency, confidence, workaround quality, regression risk, effort, and dependencies.
4. Use these levels consistently:
   - **Critical:** data loss, security exposure, unrecoverable corruption, broad outage, or a release blocker with no acceptable workaround.
   - **High:** common supported workflows are broken or materially misleading, with substantial user cost or a poor workaround.
   - **Medium:** real correctness, reliability, or documentation-contract issue with bounded impact or a reasonable workaround.
   - **Low:** uncommon edge case, clarity problem, or minor inconsistency with limited user impact.
   - **Nitpick:** polish, wording, or optional consistency improvement that does not affect successful use.
5. Do not inflate severity because an item is easy to fix, recently discovered, or personally annoying. Keep severity separate from implementation effort and mark uncertain rankings explicitly.
6. Order findings by fix priority, then severity, then confidence. Identify dependencies or items that should be fixed together, and recommend the smallest coherent first patch.

Report a compact table with rank, finding, severity, fix priority, evidence, user impact, effort, and recommended action. Follow it with:

- **Fix first:** the smallest highest-value group and why.
- **Defer or decline:** low-value, speculative, duplicate, or intentionally unsupported items.
- **Verification:** checks needed after the prioritized fixes.

Do not edit code, commit, push, publish, or mutate remote state unless the user explicitly requests those actions.
