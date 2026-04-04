---
name: create-pr
description: Run diff check, commit on a b1tank/* dev branch, push, and create a PR against main.
---

Prepare and open a pull request for the current work.

## Steps

1. **Branch check**: Run `git branch --show-current`.
   - If already on a `b1tank/*` branch, keep it.
   - Otherwise, create and switch to `b1tank/<descriptive-slug>` based on the work done (e.g., `b1tank/add-create-pr-prompt`). Derive the slug from the commit intent — don't ask.

2. **Diff check**: Run the `diff-check` skill against `main`. If critical issues are found, fix them before proceeding. Warnings are acceptable — list them but continue.

3. **Stage & commit**: Stage all changes and commit with a conventional commit message (`feat:`, `fix:`, `refactor:`, etc.). Write a clear, descriptive message — don't ask for one.

4. **Push**: `git push -u origin HEAD`.

5. **Create or update PR**: Derive **owner** and **repo** from `git remote get-url origin`.
   - **Check first**: Search for an existing open PR from the current branch to `main`.
   - **If PR exists**: Update its description (body) to reflect the full diff vs `main` after the new push. Keep the existing title unless it no longer fits.
   - **If no PR**: Create one via the GitHub MCP tool with **base** `main` and **head** as the current branch. Title: refined from the commit message.
   - **Body format**: Concise summary of *all* diffs vs `main` — not just the latest commit. Use a short paragraph or bullet list. No verbosity; a reviewer should understand the full scope in 10 seconds.

6. **Report**:
   ```
   ✅ Branch: b1tank/<name>
   ✅ Committed: <hash> — <message>
   ✅ Pushed to origin
   ✅ PR created/updated: <url>
   ```
