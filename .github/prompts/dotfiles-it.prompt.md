---
name: dotfiles-it
description: Persist selected local configuration changes in the dotfiles repository, verify them, and publish only the intended files.
argument-hint: "[configuration or file to persist]"
---

Persist the local configuration identified by the invocation input in the user's dotfiles repository. If no file is supplied, infer the relevant configuration from the current task or recent changes; ask only when the source or destination remains ambiguous.

1. Read the dotfiles repository instructions and inspect its status, layout, current branch, remotes, installer, and documentation before editing. Preserve unrelated worktree changes.
2. Compare the live configuration with its tracked counterpart. Copy only the intended, portable settings rather than blindly replacing the whole file.
3. Exclude credentials, tokens, private host or work data, machine-specific state, generated caches, and other sensitive or non-portable content. Stop and report any content that cannot be persisted safely.
4. For a newly tracked configuration, choose a conventional repository path, add an idempotent installer mapping that safely backs up an existing real file, and update the repository's file inventory. Do not overwrite or delete unrelated local configuration.
5. Verify the resulting diff, confirm that only intended files changed, and run any relevant syntax checks or repository tests. When practical, verify that installation resolves the tracked source to the expected destination without destructively reinstalling all dotfiles.
6. Stage only the intended dotfiles changes, commit them with a concise descriptive message, and push the current branch. Do not include unrelated worktree changes or force-push.
7. Report the persisted source and destination paths, verification performed, commit hash, and push result.
