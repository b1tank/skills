#!/usr/bin/env bash
# sync.sh - One script to sync this repo's agents/prompts/skills/instructions.
#
# Primary use: bidirectional sync between this repo and VS Code Insiders user-data.
#   - Repo -> user-data: copies .github/{agents,prompts,instructions} to a flat directory
#   - User-data -> repo: copies *.agent.md/*.prompt.md/*.instructions.md into .github/*
#
# Secondary use: sync this repo's .github content into another repo (.github/*).
#
# Examples:
#   ./sync.sh to-userdata --dry-run
#   ./sync.sh to-userdata --apply
#   ./sync.sh from-userdata --dry-run
#   ./sync.sh from-userdata --apply
#   ./sync.sh to-repo ~/my-project
#
# Notes:
# - Defaults to dry-run for user-data sync to avoid surprises.
# - Does NOT delete files from destinations by default.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR"

DEFAULT_USERDATA_DIR="$HOME/.config/Code/User/prompts"
DEFAULT_CODEX_SKILLS_DIR="$HOME/.codex/skills"

usage() {
    cat <<'EOF'
Usage:
    sync.sh to-userdata   [--apply|--dry-run] [--userdata <path>]
    sync.sh from-userdata [--apply|--dry-run] [--userdata <path>]
    sync.sh to-codex      [--apply|--dry-run] [--codex <path>]
    sync.sh from-codex    [--apply|--dry-run] [--codex <path>]
    sync.sh to-repo <target-repo-path>

Commands:
    to-userdata
        Copy repo files from:
            .github/agents/*.agent.md
            .github/prompts/*.prompt.md
            .github/instructions/*.instructions.md (optional)
        into the flat VS Code user-data prompts directory.

    from-userdata
        Copy user-data files from the flat directory into:
            *.agent.md         -> .github/agents/
            *.prompt.md        -> .github/prompts/
            *.instructions.md  -> .github/instructions/

    to-codex
        Copy repo skills from:
            .github/skills/
        into the Codex skills directory (default: ~/.codex/skills).

    from-codex
        Copy skills from the Codex skills directory into:
            .github/skills/

    to-repo <target>
        Copy this repo's .github/{agents,prompts,skills,instructions,copilot-instructions.md}
        into <target>/.github/.

Flags:
    --dry-run   (default for to-userdata/from-userdata/to-codex/from-codex)
    --apply     actually perform changes (no-op preview otherwise)
    --userdata  override default user-data directory
    --codex     override default Codex skills directory

EOF
}

ensure_dir() {
    local dir="$1"
    mkdir -p "$dir"
}

require_repo_layout() {
    if [[ ! -d "$REPO_DIR/.github" ]]; then
        echo "Error: expected $REPO_DIR/.github to exist." >&2
        exit 1
    fi
    if [[ ! -d "$REPO_DIR/.github/agents" ]] || [[ ! -d "$REPO_DIR/.github/prompts" ]] || [[ ! -d "$REPO_DIR/.github/skills" ]]; then
        echo "Error: expected $REPO_DIR/.github/{agents,prompts,skills} to exist." >&2
        exit 1
    fi
}

rsync_copy_flat() {
    local src_dir="$1"
    local pattern="$2"
    local dest_dir="$3"
    local dry_run_flag="$4"

    if [[ ! -d "$src_dir" ]]; then
        return 0
    fi

    local rsync_cmd=(rsync -av --prune-empty-dirs)
    if [[ -n "$dry_run_flag" ]]; then
        rsync_cmd+=("$dry_run_flag")
    fi
    rsync_cmd+=(--include="$pattern" --exclude="*" "$src_dir/" "$dest_dir/")

    "${rsync_cmd[@]}"
}

rewrite_agent_name_in_files() {
    local action="$1" # append|strip
    shift
    local files=("$@")

    local suffix=" (U)"
    local f tmp
    for f in "${files[@]}"; do
        [[ -f "$f" ]] || continue
        tmp="$(mktemp)"
        awk -v action="$action" -v suffix="$suffix" '
            {
                if (!done && $0 ~ /^[ \t]*name:[ \t]*/) {
                    if (action == "append") {
                        if ($0 !~ /\(U\)[ \t]*$/) $0 = $0 " (U)"
                    } else if (action == "strip") {
                        sub(/[ \t]*\(U\)[ \t]*$/, "", $0)
                    }
                    done = 1
                }
                print
            }
        ' "$f" > "$tmp"
        if ! cmp -s "$f" "$tmp"; then
            mv "$tmp" "$f"
        else
            rm -f "$tmp"
        fi
    done
}

command_to_userdata() {
    local userdata_dir="$1"
    local dry_run_flag="$2"

    require_repo_layout
    ensure_dir "$userdata_dir"

    echo "Sync: repo -> user-data"
    echo "  Repo:     $REPO_DIR"
    echo "  Userdata: $userdata_dir"
    echo ""

    rsync_copy_flat "$REPO_DIR/.github/agents" "*.agent.md" "$userdata_dir" "$dry_run_flag"
    rsync_copy_flat "$REPO_DIR/.github/prompts" "*.prompt.md" "$userdata_dir" "$dry_run_flag"
    rsync_copy_flat "$REPO_DIR/.github/instructions" "*.instructions.md" "$userdata_dir" "$dry_run_flag"

    if [[ -z "$dry_run_flag" ]]; then
        local copied_agents=()
        while IFS= read -r f; do
            copied_agents+=("$f")
        done < <(find "$userdata_dir" -maxdepth 1 -type f -name "*.agent.md" | sort)
        if (( ${#copied_agents[@]} > 0 )); then
            rewrite_agent_name_in_files "append" "${copied_agents[@]}"
        fi
    fi

    echo ""
    echo "Done."
}

command_from_userdata() {
    local userdata_dir="$1"
    local dry_run_flag="$2"

    require_repo_layout
    if [[ ! -d "$userdata_dir" ]]; then
        echo "Error: user-data dir does not exist: $userdata_dir" >&2
        exit 1
    fi

    ensure_dir "$REPO_DIR/.github/agents"
    ensure_dir "$REPO_DIR/.github/prompts"
    ensure_dir "$REPO_DIR/.github/instructions"

    echo "Sync: user-data -> repo"
    echo "  Userdata: $userdata_dir"
    echo "  Repo:     $REPO_DIR"
    echo ""

    rsync_copy_flat "$userdata_dir" "*.agent.md" "$REPO_DIR/.github/agents" "$dry_run_flag"
    rsync_copy_flat "$userdata_dir" "*.prompt.md" "$REPO_DIR/.github/prompts" "$dry_run_flag"
    rsync_copy_flat "$userdata_dir" "*.instructions.md" "$REPO_DIR/.github/instructions" "$dry_run_flag"

    if [[ -z "$dry_run_flag" ]]; then
        local repo_agents=()
        while IFS= read -r f; do
            repo_agents+=("$f")
        done < <(find "$REPO_DIR/.github/agents" -maxdepth 1 -type f -name "*.agent.md" | sort)
        if (( ${#repo_agents[@]} > 0 )); then
            rewrite_agent_name_in_files "strip" "${repo_agents[@]}"
        fi
    fi

    echo ""
    echo "Done."
}

command_to_codex() {
    local codex_dir="$1"
    local dry_run_flag="$2"

    require_repo_layout
    ensure_dir "$codex_dir"

    echo "Sync: repo -> codex skills"
    echo "  Repo:  $REPO_DIR/.github/skills"
    echo "  Codex: $codex_dir"
    echo ""

    local rsync_cmd=(rsync -av)
    if [[ -n "$dry_run_flag" ]]; then
        rsync_cmd+=("$dry_run_flag")
    fi
    rsync_cmd+=(--exclude='.DS_Store' --exclude='.system' --exclude='find-skills' "$REPO_DIR/.github/skills/" "$codex_dir/")

    "${rsync_cmd[@]}"

    echo ""
    echo "Done."
}

command_from_codex() {
    local codex_dir="$1"
    local dry_run_flag="$2"

    require_repo_layout
    if [[ ! -d "$codex_dir" ]]; then
        echo "Error: codex skills dir does not exist: $codex_dir" >&2
        exit 1
    fi

    ensure_dir "$REPO_DIR/.github/skills"

    echo "Sync: codex skills -> repo"
    echo "  Codex: $codex_dir"
    echo "  Repo:  $REPO_DIR/.github/skills"
    echo ""

    local rsync_cmd=(rsync -av)
    if [[ -n "$dry_run_flag" ]]; then
        rsync_cmd+=("$dry_run_flag")
    fi
    rsync_cmd+=(--exclude='.DS_Store' --exclude='.system' --exclude='find-skills' "$codex_dir/" "$REPO_DIR/.github/skills/")

    "${rsync_cmd[@]}"

    echo ""
    echo "Done."
}

command_to_repo() {
    local target_repo="$1"

    require_repo_layout
    if [[ ! -d "$target_repo" ]]; then
        echo "Error: target repo does not exist: $target_repo" >&2
        exit 1
    fi

    ensure_dir "$target_repo/.github"

    echo "Sync: this repo -> target repo"
    echo "  From: $REPO_DIR/.github"
    echo "  To:   $target_repo/.github"
    echo ""

    rsync -av \
        --exclude='.DS_Store' \
        "$REPO_DIR/.github/" \
        "$target_repo/.github/"

    echo ""
    echo "Done. Next: cd $target_repo && git status"
}

main() {
    if (( $# == 0 )); then
        usage
        exit 1
    fi

    local cmd="$1"
    shift

    local apply=false
    local userdata_dir="$DEFAULT_USERDATA_DIR"
    local codex_dir="$DEFAULT_CODEX_SKILLS_DIR"

    while (( $# > 0 )); do
        case "$1" in
            --apply)
                apply=true
                shift
                ;;
            --dry-run)
                apply=false
                shift
                ;;
            --userdata)
                userdata_dir="$2"
                shift 2
                ;;
            --codex)
                codex_dir="$2"
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

    local dry_run_flag="--dry-run"
    if [[ "$apply" == true ]]; then
        dry_run_flag=""
    fi

    case "$cmd" in
        to-userdata)
            command_to_userdata "$userdata_dir" "$dry_run_flag"
            ;;
        from-userdata)
            command_from_userdata "$userdata_dir" "$dry_run_flag"
            ;;
        to-codex)
            command_to_codex "$codex_dir" "$dry_run_flag"
            ;;
        from-codex)
            command_from_codex "$codex_dir" "$dry_run_flag"
            ;;
        to-repo)
            if (( $# < 1 )); then
                echo "Error: missing target repo path." >&2
                echo "" >&2
                usage
                exit 1
            fi
            command_to_repo "$1"
            ;;
        *)
            echo "Error: unknown command: $cmd" >&2
            echo "" >&2
            usage
            exit 1
            ;;
    esac
}

main "$@"
