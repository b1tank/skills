# Contributing

This repository is a personal but reusable cross-harness configuration. Keep changes portable, secret-free, and explicit about side effects.

Before submitting a change:

```bash
./setup.sh generate
npm test
./setup.sh bootstrap --dry-run
```

Update canonical files under `.github/`, `mcp/`, or `skills/`. Do not edit `.generated/` directly. Never commit credentials, OAuth stores, browser profiles, private outputs, generated backups, or machine-specific paths. New MCP capabilities that permit file access, process execution, or desktop mutation must remain opt-in.

By contributing, you agree that your contribution is licensed under the MIT License.
