---
description: Skills repo overview + Copilot operating guidelines
---

# Skills Repo (Entry Point)

This repository is the **source of truth** for reusable:
- Agents (`.github/agents/*.agent.md`)
- Prompts (`.github/prompts/*.prompt.md`)
- Skills (`.github/skills/*/SKILL.md`)
- Instructions (this file)

## Default Entry Point Agent

Use `@lead` as the **main orchestrator** by default.

`@lead` is responsible for:
- Turning a request into an ordered task breakdown (in chat or in a tracking issue)
- Delegating implementation to `@engineer`
- Requesting review from `@reviewer`
- Pulling in `@planner` (decomposition / sequencing) when helpful

## Syncing Agents/Prompts (VS Code UI ↔ This Repo)

VS Code stores user agents/prompts/instructions as **flat files** under:
- `~/.config/Code/User/prompts/`

This repo stores canonical versions under `.github/`.

Use the single sync script:
- Repo → user-data preview: `./sync.sh to-userdata --dry-run`
- Repo → user-data apply: `./sync.sh to-userdata --apply`
- User-data → repo preview: `./sync.sh from-userdata --dry-run`
- User-data → repo apply: `./sync.sh from-userdata --apply`

To copy these definitions into another working repo's `.github/`:
- `./sync.sh to-repo /absolute/path/to/repo`

## Operating Guidelines

### Default approach

1. **Search before coding** (semantic search for concepts, grep for exact strings, follow imports).
2. **Prefer existing patterns** over inventing new ones.
3. **Validate incrementally** (compile/lint first, then tests).

### Validation discipline

- If there are compilation/typecheck errors, fix those first.
- Prefer targeted tests over full suites.
- Don't declare work "done" while the build/watch pipeline is red.

### Quality and safety

- Don't commit or push unless explicitly requested.
- Keep changes small and reviewable.
- Avoid project-specific assumptions (hard-coded dev commands, project-specific toolchains).
- For user-facing changes: always request explicit manual verification steps when automated verification is not available.
