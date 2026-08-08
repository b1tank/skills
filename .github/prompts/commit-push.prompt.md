---
name: commit-push
description: Group the intended worktree changes into atomic commits, verify them, and push the current branch safely.
---

Commit and push the intended worktree changes.

1. Read the repository instructions and inspect the current branch, status, diff, and remote configuration. Treat any invocation input as scope, commit-message, or verification guidance.
2. Preserve unrelated changes. Identify only the files belonging to the requested work, and stop for clarification if they cannot be separated safely.
3. Check the intended diff for secrets, generated artifacts that should not be tracked, accidental edits, and repository-specific documentation or test requirements.
4. Run the relevant focused validation before committing. Do not hide or bypass failures; fix failures caused by the intended changes and report unrelated failures.
5. Divide the intended changes into the smallest coherent commits that remain independently understandable and valid. Do not split tightly coupled implementation, tests, and documentation merely to increase the commit count.
6. For each commit, stage only its exact files or hunks, review the staged diff, and use a concise conventional commit message when the repository does not require another format.
7. Push the current branch to its configured remote, setting its upstream when needed. Never force-push, switch branches, rewrite existing commits, include unrelated changes, or push to a protected branch contrary to repository policy.
8. Verify the remote update and report the validation performed, commit hashes and messages, pushed branch, and any intentionally uncommitted files.
