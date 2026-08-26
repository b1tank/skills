# Bootstrap a machine

After installing Node.js 24 or newer, at least one supported agent, and cloning this repository:

```bash
git clone https://github.com/b1tank/skills.git ~/skills
cd ~/skills
./setup.sh status
./setup.sh bootstrap
./setup.sh validate
```

`bootstrap` installs dependencies, generates portable prompt/agent projections, links skills and commands, and merges secret-free MCP definitions into detected clients. It is idempotent and backs up conflicting files before replacing them.

On a machine that already has customizations, capture anything missing from this repository first:

```bash
./setup.sh import --dry-run
./setup.sh import
git diff -- .github mcp
```

The importer copies skills and VS Code prompt files but only reports unknown MCP entries for manual, secret-safe review.

To configure only selected clients:

```bash
./setup.sh bootstrap --targets vscode,codex,claude
```

Supported target names are `vscode`, `agent-host`, `copilot`, `claude`, `codex`, `pi`, and `opencode`. VS Code's Claude and Codex harnesses consume the corresponding standalone user roots plus Agent Host configuration, so selecting `vscode-claude` expands to `vscode,agent-host,claude`; `vscode-codex` expands to `vscode,agent-host,codex`.

Credentials are intentionally absent from Git. Export the variables listed by `./setup.sh credentials`, then authenticate OAuth-capable servers with the client that uses them.

Local tool servers remain owned by their own repositories. For the complete personal setup, clone/install OTelux at `~/otelux` before bootstrap. On Linux, also clone/build Deskpal at `~/deskpal`; Deskpal is not projected on macOS or Windows because its X11/uinput implementation is Linux-only. Their MCP definitions stay centralized here, while tool-owned skill content is registered through `skills/sources.json`. Native MCP harnesses receive supported servers directly; Pi loads each supported product's thin local extension, which adapts the same MCP implementation into native Pi tools.

Pi-only utility skills are installed directly from `https://github.com/badlogic/pi-skills` into `~/.pi/agent/skills/pi-skills`. They are upstream-owned dependencies, not canonical content in this repository, and are not projected to other harnesses.

See [docs/agent-customization-compatibility.md](docs/agent-customization-compatibility.md) for paths, precedence, limitations, and troubleshooting.
