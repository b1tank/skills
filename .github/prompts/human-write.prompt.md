---
name: human-write
description: Rewrite the current pull request body into concise, natural reviewer-facing prose and publish the update.
argument-hint: "[PR body guidance]"
---

Rewrite the current branch's pull request body for human review.

- Read the repository instructions, current PR body, full branch diff, commit list, and validation results before drafting.
- Describe the actual behavior change and why it belongs at the chosen lifecycle or abstraction boundary.
- Use short, direct sentences and compact bullets. Avoid marketing language, generic filler, repetitive summaries, and claims not supported by the diff.
- Include the exact tests or checks that were run.
- State meaningful coverage limitations when they help the reviewer, including why broader coverage was not added and what existing tests cover separately.
- Preserve required attribution or disclosure text from repository instructions. Do not add optional boilerplate disclaimers unless the repository or user requires them.
- Do not change code, resolve review threads, open another PR, or alter PR state unless explicitly requested.

If the branch has authorized local commits that are not yet on its remote tracking branch, push them first. Write the body to a temporary file, update the existing PR with that file, then re-read the remote PR and verify its title, base, head, draft state, and final body. Report the PR URL and push result.
