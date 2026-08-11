#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v node >/dev/null 2>&1; then
	echo "Error: Node.js 24 or newer is required." >&2
	exit 1
fi

node_major="$(node -p 'process.versions.node.split(".")[0]')"
if (( node_major < 24 )); then
	echo "Error: Node.js 24 or newer is required (found $(node --version))." >&2
	exit 1
fi

if [[ ! -d "$repo_dir/node_modules/jsonc-parser" ]]; then
	if ! command -v npm >/dev/null 2>&1; then
		echo "Error: npm is required for the first bootstrap." >&2
		exit 1
	fi
	echo "Installing bootstrap dependencies..."
	npm --prefix "$repo_dir" ci --ignore-scripts --no-audit
fi

exec node "$repo_dir/scripts/setup.mjs" "$@"
