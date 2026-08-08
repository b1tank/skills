---
name: publish-artifact
description: Publish generated HTML, PDFs, images, reports, or artifact directories to the machine's dedicated LAN/VPN web server and return a browser-ready URL. Use when the user needs to view or download non-terminal output from another device.
---

# Publish Artifact

Publish only the artifact the user wants to share. Resolve script paths relative to this skill directory.

## Workflow

1. Identify the completed file or directory. If several candidates exist, ask which one to publish.
2. Do not publish repositories, home directories, credentials, environment files, browser profiles, database files, or unrelated outputs. Inspect the intended artifact for obvious secrets before copying it.
3. Confirm the service is healthy:

   ```bash
   systemctl --user is-active --quiet agent-artifacts.service || scripts/install-service.sh
   ```

4. Publish the artifact in snapshot mode by default:

   ```bash
   python3 scripts/publish_artifact.py <file-or-directory>
   ```

   Use `--name <slug>` when the user requests a memorable URL name. The publisher still creates a unique path and never overwrites an existing artifact.

   Use live mode only when the user explicitly asks for the published URL to reflect ongoing edits to the original file or directory:

   ```bash
   python3 scripts/publish_artifact.py --live <file-or-directory>
   ```

   Live mode links the URL to the original path. Clearly tell the user that later changes and newly added files under a live directory become immediately visible. Never choose live mode merely to avoid a small copy.
5. Verify the returned URL server-side with `curl --fail --head <url>`. If `localhost` is not resolvable locally, verify the `127.0.0.1` URL reported by `--json` instead.
6. Return the `http://localhost:8787/...` URL. Mention the IP fallback printed by the script when useful for VPN or DNS troubleshooting.

## Supported artifacts

- A single PDF, image, archive, text file, or other downloadable file is published at a direct file URL.
- A standalone HTML file is published at a direct HTML URL.
- A directory is copied intact so relative HTML, CSS, JavaScript, image, and font references continue to work. If it contains `index.html`, the returned URL opens it automatically; otherwise the server shows a directory listing.
- With explicit `--live`, the URL serves the selected original file or directory and reflects subsequent edits without republishing. The server blocks nested symbolic links that escape the selected live root.

## Artifact homepage

Open `http://localhost:8787/` for the responsive artifact library. It provides search, snapshot/live/broken filters, counts, open and copy-URL actions, refresh, and confirmed deletion. Deleting a snapshot removes only its published copy. Deleting a live publication removes only its publication link and preserves the original file or directory.

## Maintenance

List published artifacts:

```bash
python3 scripts/publish_artifact.py --list
```

Delete publications older than 30 days:

```bash
python3 scripts/publish_artifact.py --prune-days 30
```

Snapshot mode exposes only copies under `~/.local/share/agent-artifacts/public`. Opt-in live mode exposes only the explicitly selected original path, and the server prevents traversal through nested symbolic links outside that publication. The service intentionally has no application-level authentication and must remain limited to the trusted LAN/VPN by host firewall and network policy.
