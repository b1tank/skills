#!/usr/bin/env bash
set -euo pipefail

port="${AGENT_ARTIFACT_PORT:-12345}"
[[ "$port" =~ ^[1-9][0-9]{0,4}$ ]] && (( port <= 65535 )) || { echo 'Invalid port' >&2; exit 1; }
script_dir="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
server_script="$script_dir/artifact_server.py"
public_root="${AGENT_ARTIFACT_ROOT:-$HOME/.local/share/agent-artifacts/public}"
python="$(command -v python3)"
platform="$(uname -s)"
if [[ "${1:-}" == '--dry-run' ]]; then
  printf 'Platform: %s\nPython: %s\nServer: %s\nBind: 0.0.0.0:%s\nRoot: %s\n' "$platform" "$python" "$server_script" "$port" "$public_root"
  exit 0
fi
[[ $# == 0 ]] || { echo 'Usage: install-service.sh [--dry-run]' >&2; exit 1; }
mkdir -p "$public_root" "${public_root}-apps"

case "$platform" in
  Darwin)
    label="com.b1tank.agent-artifacts-$port"
    plist="$HOME/Library/LaunchAgents/$label.plist"
    mkdir -p "$(dirname "$plist")"
    "$python" - "$plist" "$label" "$python" "$server_script" "$port" "$public_root" <<'PY'
import pathlib,plistlib,sys
file,label,python,server,port,root=sys.argv[1:]
log=str(pathlib.Path(root).parent / ('artifact-service-'+port+'.log'))
with open(file,'wb') as f:
    plistlib.dump({'Label':label,'ProgramArguments':[python,server,'--bind','0.0.0.0','--port',port,'--root',root],
                  'RunAtLoad':True,'KeepAlive':True,'ThrottleInterval':3,'StandardOutPath':log,'StandardErrorPath':log},f)
PY
    launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$plist"
    launchctl kickstart "gui/$(id -u)/$label"
    ;;
  Linux)
    unit_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
    service_name="agent-artifacts-$port.service"
    mkdir -p "$unit_dir"
    "$python" - "$unit_dir/$service_name" "$python" "$server_script" "$port" "$public_root" <<'PY'
import sys
file,python,server,port,root=sys.argv[1:]
with open(file,'w') as f:
    f.write(f'''[Unit]
Description=Shared LAN artifact portal on {port}
After=network.target
[Service]
ExecStart="{python}" "{server}" --bind 0.0.0.0 --port {port} --root "{root}"
Restart=on-failure
RestartSec=2
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths="{root}" "{root}-apps"
RestrictAddressFamilies=AF_INET AF_INET6
[Install]
WantedBy=default.target
''')
PY
    systemctl --user daemon-reload
    systemctl --user enable --now "$service_name"
    systemctl --user restart "$service_name"
    systemctl --user is-active --quiet "$service_name"
    ;;
  *) echo 'Login service installation supports macOS launchd and Linux systemd only.' >&2; exit 1 ;;
esac
printf 'Artifact portal service installed: http://localhost:%s/ (bound to 0.0.0.0)\n' "$port"
