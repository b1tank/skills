# Security policy

Use GitHub private vulnerability reporting for security issues. Do not publish credentials, OAuth data, local configuration, private prompts, MCP responses, or machine-specific backups in an issue.

This repository modifies user-level configuration for multiple agent harnesses. Preview changes with `./setup.sh bootstrap --dry-run`, review the reported destinations, and keep credentials in environment variables or each client's OAuth store.

The legacy Langfuse hook is retained as reference code and is not enabled by bootstrap. If enabled manually, it can export prompts, responses, reasoning, tool activity, and subagent transcripts to the configured destination.
