# Skills bootstrap

This repository is the source of truth for the owner's cross-agent customizations.

When asked to set up, repair, synchronize, or explain agent customizations:

1. Read [BOOTSTRAP.md](BOOTSTRAP.md).
2. Preview with `./setup.sh status` and `./setup.sh bootstrap --dry-run`.
3. Run `./setup.sh bootstrap` only when the user asks to apply the setup.
4. Run `./setup.sh validate` afterward.
5. Never commit credentials. MCP credentials belong in environment variables or each client's OAuth store.

Do not edit generated files under `.generated/`; regenerate them with `./setup.sh generate`.
