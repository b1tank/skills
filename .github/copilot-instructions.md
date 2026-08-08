---
description: Personal skills repository overview and agent operating guidelines
---

# Skills Repository (Entry Point)

This repository is the source of truth for reusable:
- Agents (`.github/agents/*.agent.md`)
- Prompts (`.github/prompts/*.prompt.md`)
- Skills (`.github/skills/*/SKILL.md`)
- Instructions (this file)
- MCP definitions (`mcp/servers.json`)

It is an **entry point**: start here, then move to the appropriate target repository to implement a task.

## Machine Bootstrap

When asked to set up, repair, synchronize, or explain agent customizations, read `BOOTSTRAP.md`. Preview with `./setup.sh bootstrap --dry-run`, apply only when requested, and finish with `./setup.sh validate`. Never copy credentials into Git; MCP secrets stay in environment variables or client OAuth stores.

Edit canonical files under `.github/` and `mcp/servers.json`. Do not edit `.generated/` or projected user-directory links.

## Default Entry Point Agent

Use `@lead` as the **main orchestrator** by default.

`@lead` is responsible for:
- Turning a request into an ordered task breakdown (in chat or in a tracking issue)
- Delegating implementation to `@engineer`
- Requesting review from `@reviewer`
- Pulling in `@planner` for decomposition and sequencing when helpful

## Where to Work

Before editing anything, identify the intended local checkout or worktree from
the user's path, the current workspace, or the repository's Git remote. Do not
depend on a centrally maintained repo-to-path mapping.

If the user names a checkout or worktree explicitly, use it. Otherwise, inspect
the current workspace first, then look for a nearby checkout whose `origin`
remote matches the requested repository. Ask before cloning a new checkout or
switching a dirty working tree.

## Legacy VS Code round-trip sync

VS Code Insiders stores user agents/prompts/instructions as **flat files** under:
- `~/.config/Code - Insiders/User/prompts/`

This repo stores canonical versions under `.github/`.

Use the single sync script:
- Repo → user-data preview: `./sync.sh to-userdata --dry-run`
- Repo → user-data apply: `./sync.sh to-userdata --apply`
- User-data → repo preview: `./sync.sh from-userdata --dry-run`
- User-data → repo apply: `./sync.sh from-userdata --apply`

For normal cross-harness installation, use `./setup.sh bootstrap` instead.

To copy these definitions into another working repo’s `.github/`:
- `./sync.sh to-repo /absolute/path/to/repo`

## Operating Guidelines (VS Code–inspired)

These guidelines are adapted from the VS Code repo’s Copilot instructions (as a style reference), but are **generalized** so they apply across the repos you work in.

### Default approach

1. **Find the right repo + folder** (use the mapping table).
2. **Search before coding** (semantic search for concepts, grep for exact strings, follow imports).
3. **Prefer existing patterns** over inventing new ones.
4. **Validate incrementally** (compile/lint first, then tests).

### Validation discipline

- If there are compilation/typecheck errors, fix those first.
- Prefer targeted tests over full suites.
- Don’t declare work “done” while the build/watch pipeline is red.

### Quality and safety

- Don’t commit or push unless explicitly requested.
- Keep changes small and reviewable.
- Avoid personal-project-specific assumptions (hard-coded dev commands, project-specific toolchains).
- For user-facing changes: always request explicit manual verification steps when automated verification is not available.

### Typical daily workflows this repo should support

- Issue triage (summarize, repro ask, labels, dedupe, route to owner)
- PR authoring (clear description, tests, screenshots if applicable)
- PR review (correctness, performance, layering/architecture, test coverage)
- Release notes (summarize commit/PR history into user-facing bullets)
