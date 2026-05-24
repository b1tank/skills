# b1tank/skills

Reusable AI agent skills, agents, and prompts for the [skills.sh](https://skills.sh) ecosystem.

**[ARCHITECTURE.md](ARCHITECTURE.md)** — The golden guide for agent/skill/prompt architecture design.

## Structure

```
ARCHITECTURE.md          # Golden architecture reference guide
sync.sh                  # Bidirectional sync (VS Code user-data, Codex, other repos)
.claude/hooks/           # Claude Code hooks
  └── langfuse_hook.py   # Langfuse tracing for Claude Code sessions

.github/
  ├── copilot-instructions.md  # Repo-wide rules
  ├── agents/                  # Shareable agent definitions
  │   ├── engineer.agent.md    # Dedicated implementation
  │   ├── explainer.agent.md   # Educational code explanations
  │   ├── lead.agent.md        # Tech lead: orchestration
  │   ├── planner.agent.md     # Task breakdown & sequencing
  │   ├── product-designer.agent.md  # spec.md from idea
  │   ├── reviewer.agent.md    # Critical "grill me" review
  │   └── ui-tester.agent.md   # UI verification
  │
  ├── prompts/                 # Shareable prompts
  │   ├── continue-in-new.prompt.md   # Session handoff
  │   ├── create-pr.prompt.md         # Diff-check + PR
  │   ├── grill-me-for-pr.prompt.md   # Pre-PR readiness
  │   ├── new-agent.prompt.md         # Create new agent → @lead
  │   ├── new-project.prompt.md       # New project → @product-designer
  │   ├── self-improve.prompt.md      # Meta improvement
  │   ├── sprint-in-yolo.prompt.md    # Autonomous sprint
  │   ├── verify-ux.prompt.md         # UX verification
  │   └── work-on-next.prompt.md      # Next task → triage/plan/impl
  │
  └── skills/                  # Shareable skills
      ├── clone-with-hash/     # Isolated repo clones for parallel work
      ├── decompose-task/      # Break large tasks into atomic sub-tasks
      ├── diff-check/          # Author cleanup before commit/PR submit
      ├── ios-safari-debug/    # Debug iPhone Safari from Linux (no Mac needed)
      ├── market-research/     # Research products/competitors
      └── spec-template/       # 9-section product spec pattern
```

## Installation

### Skills (automatic via npx)

```bash
npx skills add b1tank/skills
```

This installs all skills from `.github/skills/` to `~/.copilot/skills/`.

### Agents & Prompts (sync to VS Code user-data)

```bash
# Preview what will change
./sync.sh to-userdata --dry-run

# Apply
./sync.sh to-userdata --apply
```

When syncing **to user-data**, agent names are suffixed with ` (U)` so they're visually distinct in VS Code. When syncing **from user-data** back, that suffix is stripped.

### Copy into another repo

```bash
./sync.sh to-repo ~/my-project
```

### Codex skills sync

```bash
./sync.sh to-codex --apply    # repo → ~/.codex/skills
./sync.sh from-codex --apply  # ~/.codex/skills → repo
```

## Creating New Skills

1. Copy `template/SKILL.md` to `.github/skills/<name>/SKILL.md`
2. Update the YAML frontmatter (name, description)
3. Write the skill instructions
4. Push to GitHub
5. Install: `npx skills add b1tank/skills`

## Common Prompts

- `/work-on-next` — start work on a new issue/bug/feature (triage, planning, or implementation)
- `/new-project` — draft a `spec.md` from a one-liner
- `/create-pr` — diff-check, commit, push, create PR
- `/grill-me-for-pr` — pre-PR readiness review
- `/sprint-in-yolo` — execute full sprint autonomously
- `/continue-in-new` — document state for session handoff

## Reference

Based on [anthropics/skills](https://github.com/anthropics/skills/tree/main) structure.
