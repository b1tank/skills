---
name: serve
description: Serve HTML pages, interview guides, PDFs, images, static bundles, or approved local web apps through one LAN/VPN artifact portal. Use for /serve, serve this, open this HTML, publish an artifact, or view/download output on a phone or another device. Default 0.0.0.0:12345; do not ask the user to repeat bind addresses or ports.
compatibility: Python 3.10+ on macOS/Linux; optional launchd/systemd login service.
---

# Serve — one bookmark for artifacts and apps

Use **one shared portal bound to `0.0.0.0:12345`**. Its storage remains `~/.local/share/agent-artifacts/public`, so existing publications survive the port/skill rename. `0.0.0.0` is a listening address, not a browser URL. Return the actual LAN URL for phone use, plus localhost for the workstation.

Resolve every bundled script path relative to this skill directory. The only user-facing workflow is `/serve`; `publish_artifact.py` is an internal snapshot/live implementation, not a separate skill.

## Invocation

- `/serve`: select the clearly identified output from the current task. If there is no output to publish, open/ensure the portal. Ask only if several artifacts are genuinely ambiguous.
- `/serve report.html`: publish the page; include its required relative assets as a deliberate output bundle when needed.
- `/serve www/`: publish only that bundle, never its parent repository.
- `/serve a.html b.html`: create separate portal cards.
- `/serve --live www/`: explicitly track subsequent edits; warn that new files under that approved root also become reachable.
- `/serve --app <local-url> --name <title>`: register an approved backend application's LAN link in the same portal.
- `/serve --list`: show publications and app reachability.
- An explicit `--port` or `AGENT_ARTIFACT_PORT` overrides 12345. Never silently choose a different port or kill an unrelated listener.

## Static artifacts: default workflow

1. Identify the completed file/bundle. Inspect it for credentials, private unrelated material, missing assets and root-relative API/worker paths. Do not publish home/repository roots, browser profiles, environment files, raw restricted research, or unrelated application/candidate files.
2. Run the single entry point (it starts/reuses the dedicated server automatically):

   ```bash
   python3 scripts/serve.py <file-or-directory> --json
   ```

   Add `--name <slug>` for a readable title, or `--live` only when explicitly requested. Snapshots are immutable copies and never overwrite old publications. Do not auto-delete older versions or other portal entries.
3. Verify the returned artifact URL using `curl --fail --head`; use the `local_url`/127.0.0.1 form for server-side verification.
4. Return the artifact's LAN URL and the shared LAN portal bookmark. Do not return only localhost when the user wants a phone/other device. Retain fragments such as `#appearances` when useful.

The helper refuses occupied ports unless the listener identifies itself as the expected all-interface portal for the same storage root. It never shuts down another service. It launches a detached process, so closing the agent/terminal does not stop the portal. For login/reboot persistence, use `scripts/install-service.sh` when requested (launchd on macOS, systemd user service on Linux).

## Static versus application

Interactive JavaScript or browser Python does not automatically require a custom server: a complete static bundle can share this portal. A page needing APIs, workspace writes, SSE, WebSocket signaling, or server execution needs its documented backend; copying its HTML alone is insufficient.

For an explicitly requested, trusted application:

1. Read its startup documentation and security constraints. Explain/get approval before newly exposing filesystem writes, inference jobs or other sensitive actions to the LAN. Do not disable authentication, tokens or Host/Origin checks.
2. Start/reuse the documented backend with an approved LAN bind and any required allow-host/origin settings. Check port availability; never stop unrelated apps. Do not execute arbitrary commands from a webpage or an unreviewed manifest.
3. Verify the app locally and over the LAN, including required browser capabilities. WebRTC/camera/microphone generally require trusted HTTPS on a phone; registering a link does not solve TLS or media transport.
4. Register it, without copying its code/data:

   ```bash
   python3 scripts/serve.py --app http://127.0.0.1:8765/ --name "Meta AI Coding Lab" --json
   ```

The helper checks that the local backend is running and, when LAN addresses are available, reachable through a LAN interface. Portal app links substitute the hostname used to open the portal, so phone clients do not navigate to their own localhost. The card shows TCP reachability (running/stopped), not a comprehensive application health guarantee. Deleting an app card unregisters the link; it does not stop the process or delete its files.

**One bookmark, not necessarily one backend port:** this implementation uses registered app links. It is not a universal reverse proxy and does not rewrite `/api`, `/runtime`, cookies, Origin rules, SSE or WebSockets. Do not claim arbitrary apps work beneath a path prefix. Backends remain separate browser origins, avoiding accidental same-origin access from every HTML artifact to writable app APIs.

## Portal, safety and maintenance

- Portal: `http://<LAN-IP-or-hostname>:12345/`. Prefer a stable LAN hostname/DHCP reservation for a lasting phone bookmark.
- Search, snapshot/live/app/offline filters, open/copy and confirmed deletion are available. Newest publications appear top-left using publication time, not copied source mtimes. Legacy non-timestamped entries fall back to modification time.
- Snapshot deletion removes only its copy; live deletion removes only the link. Registrations are outside the served root. Nested symlink escapes are blocked.
- The service has no login. Use only trusted LAN/VPN/firewall boundaries and trusted HTML; never expose it publicly. Do not run untrusted browser Python with secrets.
- Existing machines may retain **8787 as an explicit compatibility listener** over the same storage. Do not remove it without permission. New publications use 12345 by default; no data migration is needed.
- Internal CLI `python3 scripts/publish_artifact.py --list` lists static publications. Destructive `--prune-days` is available only on explicit request; do not use it for automatic cleanup.

## Validate

```bash
python3 -m unittest discover -s tests -v
```

Check real HTTP and, when browser access is available, the portal/app links from desktop/mobile. Disclose unavailable visual checks rather than claiming them.
