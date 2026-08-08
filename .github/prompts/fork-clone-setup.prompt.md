---
name: fork-clone-setup
description: Fork one or more upstream repositories with the requested GitHub account, clone them locally, and configure verified origin and upstream remotes.
argument-hint: "<repository URLs, account, and destination>"
---

Fork the supplied GitHub repositories with the requested account and prepare local clones for development.

1. Read any applicable workspace and repository instructions. Inspect each intended destination before changing local or remote state.
2. Verify the GitHub CLI's effective API identity for the requested account. Account switching alone is not sufficient when wrappers or environment tokens may override authentication. Do not print or persist credentials.
3. For each repository:
   - Confirm the canonical upstream owner, repository, and default branch.
   - Create or reuse the requested account's fork without changing repository visibility or settings.
   - Clone the fork into the intended local destination. If that path already exists, do not overwrite, delete, or reclone it. Reuse it only when it is a clean clone of the same upstream; otherwise stop and report the conflict.
   - Configure `origin` to fetch from and push to the requested account's fork.
   - Configure `upstream` to fetch from the canonical repository. Do not push to upstream.
   - Fetch both remotes and make the local default branch track the fork's matching default branch.
4. Verify each setup by reporting the local path, current branch and status, fork URL, upstream URL, remote mappings, and tracking branch. Ensure no unrelated local changes were introduced.

Do not delete repositories, alter existing forks, modify authentication scopes, or perform other external actions unless the user explicitly authorizes them. If an unintended external mutation occurs, attempt only a safe, already-authorized rollback; otherwise report it clearly.
