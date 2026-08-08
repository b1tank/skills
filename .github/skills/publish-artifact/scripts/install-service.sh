#!/usr/bin/env bash
set -euo pipefail

service_name="agent-artifacts.service"
unit_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
unit_file="$unit_dir/$service_name"
public_root="${AGENT_ARTIFACT_ROOT:-$HOME/.local/share/agent-artifacts/public}"
global_server="$HOME/.agents/skills/publish-artifact/scripts/artifact_server.py"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
server_script="$script_dir/artifact_server.py"

if [[ -f "$global_server" ]]; then
	server_script="$global_server"
fi
if [[ ! -x /usr/bin/python3 ]]; then
	echo "install-service: /usr/bin/python3 is required" >&2
	exit 1
fi

mkdir -p "$unit_dir" "$public_root"
chmod 0755 "$public_root"

cat >"$unit_file" <<EOF
[Unit]
Description=Serve agent-generated artifacts to the trusted LAN/VPN
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $server_script --bind 0.0.0.0 --port 8787 --root $public_root
Restart=on-failure
RestartSec=2
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$public_root
RestrictAddressFamilies=AF_INET AF_INET6

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable "$service_name"
systemctl --user restart "$service_name"
systemctl --user is-active --quiet "$service_name"
printf 'Artifact server installed: http://localhost:8787/\n'
