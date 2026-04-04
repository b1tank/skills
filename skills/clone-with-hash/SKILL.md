---
name: clone-with-hash
description: Clone a local or remote git repo into a new folder with a short random hash suffix (e.g., -a1b2c3) and immediately create a new branch from a base branch. Use when a user wants a separate workspace to avoid conflicts, especially for parallel feature work or multiple local clones.
---

# Clone With Hash

## Overview

Create a fresh git clone in a unique `-<hash>` folder under a chosen parent directory (default: home), then check out a new branch from `origin/main` (or another base branch if specified).

## Workflow

1) Identify the source repo (local path or remote URL).
2) Choose the parent directory (default: `~`) and suffix length (default: 6).
3) Derive the base name from the repo path or URL (strip trailing `.git`).
4) Generate a random hex suffix, build the destination path, and ensure it does not exist.
5) Run `git clone <src> <dest>`, then `git checkout -b <branch> origin/<base>`.
6) Report the destination path and created branch.

## Quick Commands

```bash
python - <<'PY'
import os, secrets
src = "/path/to/repo-or-url"
parent = os.path.expanduser("~")
name = os.path.basename(src).removesuffix(".git")
suffix = secrets.token_hex(3)  # 6 hex chars
print(os.path.join(parent, f"{name}-{suffix}"))
PY
```

```bash
git clone /path/to/repo-or-url ~/repo-name-<hash>
git -C ~/repo-name-<hash> checkout -b user/<random> origin/main
```

## Script

Use the bundled helper if you want a consistent, repeatable command:

```bash
./scripts/clone_with_hash.sh [--base <branch>] [--branch-prefix <prefix>] <repo-path-or-url> [parent-dir] [suffix-len]
```

Examples:

```bash
./scripts/clone_with_hash.sh /home/user/my-project
./scripts/clone_with_hash.sh https://github.com/org/repo.git ~/workspaces 8
./scripts/clone_with_hash.sh --base main --branch-prefix user/ /home/user/my-project
./scripts/clone_with_hash.sh --dry-run /home/user/my-project
```

## Notes

- If the source path is not a git repo, ask whether a plain directory copy is acceptable before proceeding.
- If the destination already exists, generate a new suffix or choose a different parent directory.
