# Agent customization compatibility

`b1tank/skills` is the canonical, secret-free source. `./setup.sh bootstrap` projects it into each client's user scope; do not hand-maintain projected links.

## Compatibility matrix

| Harness | Skills | Slash prompts / commands | Custom agents | Instructions | MCP configuration |
| --- | --- | --- | --- | --- | --- |
| VS Code Insiders (Copilot) | `~/.agents/skills/*/SKILL.md` | `~/.config/Code - Insiders/User/prompts/*.prompt.md` | Same directory, `*.agent.md` | Same directory, `*.instructions.md`; workspace `.github/copilot-instructions.md` | `~/.config/Code - Insiders/User/mcp.json` |
| VS Code Agent Host | `~/.agents/skills/*/SKILL.md` | Canonical VS Code prompt files; prompts are also generated as skills | Canonical VS Code agents; provider adapters translate supported customizations | Repository instructions plus independently managed provider user instructions | `~/.config/Code - Insiders/User/globalStorage/agent-host-config.json` under `mcpServers` |
| VS Code Claude harness | Shared skills plus `~/.claude/skills` | `~/.claude/commands/*.md` | `~/.claude/agents/*.md` | Repository `CLAUDE.md`; user-global instructions are not managed here | Agent Host MCP plus Claude user MCP |
| VS Code Codex harness | `~/.agents/skills` and Codex discovery | Prompts generated as skills | `~/.codex/agents/*.toml` | Repository `AGENTS.md`; user-global instructions are not managed here | Agent Host MCP plus Codex user MCP |
| Copilot CLI | `~/.agents/skills` (also supports `~/.copilot/skills`) | `~/.claude/commands/*.md` is supported natively; prompts are also generated as skills | `~/.copilot/agents/*.agent.md` | Nearest repository `AGENTS.md`; user-global instructions are not managed here | `~/.copilot/mcp-config.json` |
| Claude Code | `~/.claude/skills/*/SKILL.md` | `~/.claude/commands/*.md` | `~/.claude/agents/*.md` | Repository `CLAUDE.md`; user-global instructions are not managed here | `~/.claude.json` (`$CLAUDE_CONFIG_DIR/.claude.json` when set) |
| Codex CLI / app | `~/.agents/skills`; `$CODEX_HOME/skills` is reserved for legacy, system, and plugin assets | No general command-file surface; every prompt is generated as an explicitly triggered skill | `~/.codex/agents/*.toml` | Nearest repository `AGENTS.md`; user-global instructions are not managed here | `~/.codex/config.toml` under `mcp_servers` |
| Pi | `~/.agents/skills` (native Agent Skills support) | `~/.pi/agent/prompts/*.md` | No equivalent projection currently; prompt/skill workflows remain available | Repository `AGENTS.md`; `~/.pi/agent/AGENTS.md` is not managed here | No native MCP client; the repo-local MCPorter CLI can use the generated `.generated/mcporter.json` registry when explicitly requested |
| OpenCode | `~/.agents/skills` | `${XDG_CONFIG_HOME:-~/.config}/opencode/commands/*.md` | `${XDG_CONFIG_HOME:-~/.config}/opencode/agents/*.md` | Repo `AGENTS.md` | `${XDG_CONFIG_HOME:-~/.config}/opencode/opencode.jsonc` under `mcp` |

Linux paths are shown. VS Code user data maps to `~/Library/Application Support/Code - Insiders/User` on macOS and `%APPDATA%/Code - Insiders/User` on Windows. Set `VSCODE_INSIDERS_USER_DATA_DIR` to override it.

## What the similarly named directories mean

| Path | Meaning |
| --- | --- |
| `.github/` | Canonical files in this repo and Copilot-compatible project customizations. In `b1tank/skills`, edit these files. |
| `.agents/` / `~/.agents/` | Vendor-neutral Agent Skills location. The installer uses `~/.agents/skills` as the main shared projection. |
| `.claude/` / `~/.claude/` | Claude project/user customizations. Copilot CLI also deliberately reads Claude single-file commands. |
| `.codex/` / `~/.codex/` | Codex project/user configuration, agents, and Codex-only skills. MCP belongs in `config.toml`. |
| `.copilot/` / `~/.copilot/` | Copilot CLI project/user agents, instructions, plugins, and MCP. |
| `.vscode/` | Settings for one workspace. `.vscode/mcp.json` is intentionally repo-specific and is not centralized here. |
| `~/.config/` | Linux XDG application data, including VS Code Insiders user data and OpenCode. It is not a cross-agent standard. |

## Canonical-to-projected flow

| Canonical source | Generated or installed result |
| --- | --- |
| `.github/skills/<name>/` | Linked into `~/.agents/skills`; also into Claude's required vendor-specific skill root |
| `skills/sources.json` | Registers skills owned by sibling tool repositories, such as OTelux, into the same shared projection without copying their source |
| `.github/prompts/<name>.prompt.md` | Native VS Code prompt; argument-forwarding command Markdown for Claude, Copilot, Pi, and OpenCode; invocation-aware `SKILL.md` for Codex and any skill-aware harness |
| `.github/agents/<name>.agent.md` | Native VS Code/Copilot agent; generated Claude, Codex, and OpenCode agent formats |
| `.github/instructions/*.instructions.md` | VS Code user instruction files |
| `mcp/servers.json` | Merged into native MCP files and rendered as `.generated/mcporter.json` for Pi |
| `AGENTS.md` / `CLAUDE.md` | Repository-local only; read when an agent opens this repo and never projected into user instruction roots |

`.generated/` is disposable and ignored by Git. Regenerate it; never edit it.

## Skill location policy

Use `~/.agents/skills` as the only ordinary user-skill projection for VS Code, Agent Host, Copilot CLI, Codex, Pi, and OpenCode. Their current implementations all discover that vendor-neutral Agent Skills location. Codex still reads `$CODEX_HOME/skills`, but its source labels that user location deprecated; keep it for Codex system/plugin assets, not personal cross-agent skills.

Claude Code does not currently discover `~/.agents/skills`, so bootstrap projects the same canonical sources into `~/.claude/skills`. This is a compatibility adapter, not a second source of truth. Never edit either projection directly.

Tool-owned skills stay in the owning repository. `skills/sources.json` lets bootstrap link them into the shared registry. OTelux therefore owns its four observability skills while `b1tank/skills` owns where each harness discovers them.

## Tool availability policy

| Tool | Scope | Delivery |
| --- | --- | --- |
| Slack | Copilot CLI and VS Code Agent Host only | Copilot plugin; deliberately absent from the canonical MCP registry and from Claude/Codex plugins |
| Deskpal | Every harness | Native clients receive the `deskpal` stdio MCP entry; Pi loads Deskpal's thin product-owned extension, which preserves native image results and session cleanup |
| OTelux | Every harness | Native clients receive the `otelux` stdio bridge plus tool-owned skills; Pi loads OTelux's thin product-owned extension over the same bridge |

Pi intentionally has no built-in MCP client. Its author recommends ordinary CLI tools for progressive disclosure and specifically points MCP users to MCPorter. The generated `.generated/mcporter.json` has `imports: []`, so Pi sees exactly the target-filtered canonical registry and does not accidentally import Slack or plugin-only servers from another harness. Deskpal and OTelux are excluded from that Pi registry because their product-owned extensions expose the same MCP tools natively without a second server implementation.

Pi discovers both `~/.pi/agent/skills` and `~/.agents/skills`, with the former winning name collisions. Bootstrap installs Badlogic's upstream `pi-skills` checkout only under `~/.pi/agent/skills/pi-skills`, while canonical personal skills remain under `~/.agents/skills`. It archives legacy `obstudio` containers and direct duplicates of canonical skills from the Pi-specific root. Upstream Pi-only skills are not copied into this repository or projected to other harnesses.

User-authored prompt workflows such as `/sprint-in-yolo` and `/diff-check` use the concise `/name` form in Pi and are generated as skills for harnesses without a native prompt-command surface. Canonical prompts can declare an `argument-hint` when autocomplete guidance is useful. Bootstrap always injects `$ARGUMENTS` into the Claude/Copilot/Pi/OpenCode command projections so trailing input such as `/sprint-in-yolo fix the settings regression` is preserved. Skill projections instead tell the agent to consume additional text from the explicit invocation because skill-capable harnesses retain that text as user input rather than expanding command-template variables. VS Code uses its native prompt invocation input and `argument-hint`. Third-party and tool-provided capabilities such as Brave Search and OTelux remain ordinary Pi `/skill:name` commands. Bootstrap excludes only the generated copies of personal prompt workflows from Pi skill discovery, preventing duplicate autocomplete entries without changing Pi's native skill behavior.

Deskpal and OTelux are local sibling tools. On a new machine, place their checkouts at `~/deskpal` and `~/otelux`, build/install them according to their own documentation, and then run bootstrap. `./setup.sh validate` warns when a local MCP executable or external skill source is missing.

## Precedence and reload rules

- Project customizations normally refine or override user customizations. Keep project-specific MCP in `.vscode/mcp.json` or the target client's project config rather than adding it globally.
- `AGENTS.md` and `CLAUDE.md` remain repository-local. Bootstrap does not manage user-global instruction files; it removes only historical symlinks from this repository that older versions installed.
- Existing files at link destinations are moved into timestamped archives under `~/.config/b1tank-skills/backups/`, outside every discovery root. Legacy `*.work-skills-backup-*` entries are migrated there automatically. JSON, JSONC, and TOML MCP files are merged instead of replaced. The installer records its managed MCP names in `~/.config/b1tank-skills/state.json`, so deleting a canonical server also prunes only that server from later projections.
- Start a new chat/session after changing skills, commands, agents, or instructions. Restart VS Code after changing user prompts or Agent Host MCP configuration.
- MCP credentials never belong in this repository. Run `./setup.sh credentials`, export the named variables, and use client OAuth where available.

## Machine lifecycle

On a new machine:

```bash
git clone git@github.com-b1tank:b1tank/skills.git ~/skills
cd ~/skills
./setup.sh status
./setup.sh bootstrap --dry-run
./setup.sh bootstrap
./setup.sh validate --connect
```

On an existing machine, first run `./setup.sh import --dry-run`, then `./setup.sh import` to capture previously untracked skills/prompts. Review the Git diff before committing. MCP import is intentionally review-only so credentials cannot be copied accidentally.

To add a customization later:

1. Add or edit the canonical file under `.github/` or `mcp/servers.json`.
2. Keep secrets as environment-variable names in the MCP manifest.
3. Run `./setup.sh generate`, `./setup.sh validate`, and `./setup.sh bootstrap`.
4. Start fresh agent sessions and validate the relevant MCP server/tool.
5. Commit only canonical sources and the lockfile—not `.generated/`, credentials, or backups.
