#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'USAGE'
Usage:
    clone_with_hash.sh [--dry-run] [--base <branch>] [--branch-prefix <prefix>] <repo-path-or-url> [parent-dir] [suffix-len]

Examples:
    clone_with_hash.sh /home/user/my-project
    clone_with_hash.sh https://github.com/org/repo.git ~/workspaces 8
    clone_with_hash.sh --dry-run /home/user/my-project
    clone_with_hash.sh --base main --branch-prefix user/ /home/user/my-project
USAGE
}

dry_run=false
base_branch="main"
branch_prefix="b1tank/"

while (( $# > 0 )); do
    case "${1:-}" in
        --dry-run)
            dry_run=true
            shift
            ;;
        --base)
            base_branch="${2:-}"
            shift 2
            ;;
        --branch-prefix)
            branch_prefix="${2:-}"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

src="${1:-}"
parent="${2:-$HOME}"
suffix_len="${3:-6}"

if [[ -z "$src" ]]; then
    usage
    exit 1
fi

if [[ ! -d "$parent" ]]; then
    echo "Error: parent directory does not exist: $parent" >&2
    exit 1
fi

if ! [[ "$suffix_len" =~ ^[0-9]+$ ]] || (( suffix_len <= 0 )); then
    echo "Error: suffix length must be a positive integer." >&2
    exit 1
fi

base="$(basename "$src")"
base="${base%.git}"

hash="$(python - "$suffix_len" <<'PY'
import secrets, sys
n = int(sys.argv[1])
bytes_len = (n + 1) // 2
print(secrets.token_hex(bytes_len)[:n])
PY
)"

branch="${branch_prefix}${hash}"

dest="$parent/${base}-${hash}"

if [[ -e "$dest" ]]; then
    echo "Error: destination already exists: $dest" >&2
    exit 1
fi

if [[ "$dry_run" == "true" ]]; then
    echo "$dest"
    exit 0
fi

git clone "$src" "$dest"

if git -C "$dest" show-ref --verify --quiet "refs/heads/$branch"; then
    echo "Error: branch already exists: $branch" >&2
    exit 1
fi

if ! git -C "$dest" show-ref --verify --quiet "refs/remotes/origin/$base_branch"; then
    echo "Error: base branch not found: origin/$base_branch" >&2
    echo "Hint: pass --base <branch> or create the branch manually." >&2
    exit 1
fi

git -C "$dest" checkout -b "$branch" "origin/$base_branch"
echo "$dest"
