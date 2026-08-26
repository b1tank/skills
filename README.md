# b1tank/skills

My portable AI-agent setup: reusable skills, prompt workflows, custom agents,
instructions, and MCP definitions shared across the coding tools I use.

The repository is an opinionated personal configuration rather than a general
framework. Its main goal is to keep one reviewed source of truth instead of
maintaining a different copy for every agent harness.

> **Early open-source release.** The bootstrap and tests are exercised on macOS
> and Ubuntu Linux. Omarchy, Arch Linux, and Windows have not yet been separately
> qualified. Always run the dry-run first. Deskpal and OTelux integrations are
> optional and require their sibling repositories; process execution and file
> access remain opt-in.

## Supported harnesses

The bootstrap currently projects compatible customizations into:

- Visual Studio Code Insiders and VS Code Agent Host
- GitHub Copilot CLI
- Claude Code
- Codex
- Pi
- OpenCode

Most harnesses discover shared skills from the vendor-neutral
`~/.agents/skills` directory. Claude receives an additional compatibility
projection. Prompt workflows are generated as commands or explicitly triggered
skills according to what each harness supports.

See the [compatibility matrix](docs/agent-customization-compatibility.md) for
exact paths, precedence, and known limitations.

## What is included

- `.github/skills/`: reusable procedures with any supporting scripts or references
- `.github/prompts/`: slash-style workflows such as `/diff-check`, `/de-ai`, and `/polish-wording`
- `.github/agents/`: focused roles for engineering, planning, review, explanation, and UI testing
- `.github/instructions/`: scoped VS Code instruction files
- `mcp/servers.json`: secret-free MCP server definitions
- `skills/sources.json`: optional skills owned by sibling local tools
- `scripts/setup.mjs`: cross-harness generation, installation, backup, and validation

Generated projections live under `.generated/` and are intentionally ignored.
Edit canonical files, then run `./setup.sh generate` rather than editing a
projection directly.

## Set up a machine

Requirements:

- Node.js 24 or newer
- At least one supported agent harness
- Git

Clone the repository and inspect what bootstrap would change:

```bash
git clone https://github.com/b1tank/skills.git ~/skills
cd ~/skills
./setup.sh status
./setup.sh bootstrap --dry-run
```

Apply and validate the setup:

```bash
./setup.sh bootstrap
./setup.sh validate
```

Bootstrap is idempotent. It links canonical content, generates portable
projections, merges secret-free MCP definitions into detected clients, and
backs up conflicting files before replacing them.

For complete setup behavior, selective targets, importing existing
customizations, and credential handling, read [BOOTSTRAP.md](BOOTSTRAP.md).
The design and ownership boundaries are described in
[ARCHITECTURE.md](ARCHITECTURE.md).

## Credentials and local integrations

Credentials are never stored in this repository. `mcp/servers.json` names the
environment variables required by a server, while actual values belong in the
shell environment or a client's OAuth store. Run this command to see what the
current configuration expects:

```bash
./setup.sh credentials
```

OTelux and Deskpal integrations are optional and expect those products to be
installed in sibling directories. Unsupported platforms and missing optional
products are skipped or reported by validation rather than copied into this
repository.

## Legacy Langfuse hook

`.claude/hooks/langfuse_hook.py` is retained as a legacy reference
implementation. Bootstrap does not install or enable it. The hook can export
prompts, responses, reasoning, tool activity, and subagent transcripts to a
configured Langfuse destination, so it should remain disabled unless that
content and destination are explicitly trusted. API keys are read only from
environment variables and are not included here.

## Development

Regenerate projections:

```bash
./setup.sh generate
```

Run repository tests:

```bash
npm test
```

Inspect setup without applying it:

```bash
./setup.sh bootstrap --dry-run
```

`sync.sh` remains for its older bidirectional VS Code and copy-to-repository
workflows. Prefer `setup.sh` for machine-wide installation.

## License

Licensed under the [MIT License](LICENSE).
