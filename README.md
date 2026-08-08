# b1tank/skills

One source of truth for personal agent skills, slash prompts, custom agents, instructions, and MCP servers across VS Code Insiders, VS Code Agent Host, Copilot CLI, Claude Code, Codex, Pi, and OpenCode. Shared skills use the vendor-neutral `~/.agents/skills` location wherever supported; Claude receives a compatibility projection. Pi accesses MCP through the token-efficient MCPorter CLI rather than a generic MCP extension.

## New machine

Install any one supported agent, then:

```bash
git clone git@github.com-b1tank:b1tank/skills.git ~/skills
cd ~/skills
./setup.sh status
./setup.sh bootstrap --dry-run
./setup.sh bootstrap
./setup.sh validate --connect
```

After that, every supported harness sees the same customizations. An agent opened in this repo reads `AGENTS.md` or `CLAUDE.md` and knows how to set up or repair the machine for all other agents.

## Canonical content

- `.github/skills/*/SKILL.md` — reusable skills
- `.github/prompts/*.prompt.md` — slash workflows such as `/diff-check` and `/sprint-in-yolo`; generated as commands or skills when necessary
- `.github/agents/*.agent.md` — custom roles
- `.github/instructions/*.instructions.md` — VS Code instruction files
- `mcp/servers.json` — secret-free MCP definitions
- `AGENTS.md` and `CLAUDE.md` — repository-local bootstrap instructions, discovered only when an agent works in this repo; bootstrap never installs them as user-global instructions

Use `./setup.sh import --dry-run` on an already-customized machine to find skills and prompt files missing from Git. Use `./setup.sh credentials` to list required environment variables.

See [BOOTSTRAP.md](BOOTSTRAP.md) for commands and [the compatibility matrix](docs/agent-customization-compatibility.md) for every path, format, precedence rule, and limitation. [ARCHITECTURE.md](ARCHITECTURE.md) explains the design.

`sync.sh` remains for its old bidirectional VS Code and copy-to-repo workflows. Prefer `setup.sh` for machine-wide installation.
