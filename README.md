# b1tank/skills

Portable skills, prompts, agents, instructions, and MCP configuration for the AI coding tools I use.

## Supported tools

- Visual Studio Code Insiders and VS Code Agent Host
- GitHub Copilot CLI
- Claude Code
- Codex
- Pi
- OpenCode

See the [compatibility matrix](docs/agent-customization-compatibility.md) for paths and limitations.

## Contents

- `.github/skills/`: reusable skills
- `.github/prompts/`: prompt workflows
- `.github/agents/`: specialized agents
- `.github/instructions/`: scoped VS Code instructions
- `mcp/servers.json`: MCP server definitions
- `skills/sources.json`: skills provided by optional local tools
- `scripts/setup.mjs`: setup, generation, backup, and validation

Generated files live in `.generated/`. Edit the canonical files and regenerate them instead of editing projections directly.

## Setup

Requires Node.js 24 or newer, Git, and at least one supported tool.

```bash
git clone https://github.com/b1tank/skills.git ~/skills
cd ~/skills
./setup.sh bootstrap --dry-run
./setup.sh bootstrap
./setup.sh validate
```

See [BOOTSTRAP.md](BOOTSTRAP.md) for selective targets, imports, and credentials. See [ARCHITECTURE.md](ARCHITECTURE.md) for design details.

## Security

Credentials are not stored in this repository. MCP credentials must come from environment variables or client OAuth stores. List expected variables with:

```bash
./setup.sh credentials
```

The legacy `.claude/hooks/langfuse_hook.py` is retained as a reference and is not installed by bootstrap.

## Development

```bash
./setup.sh generate
npm test
```

## License

[MIT](LICENSE)
