# b1tank/skills

Reusable AI agent skills, agents, and prompts for the [skills.sh](https://skills.sh) ecosystem.

## Structure

```
skills/              # Shareable skills (npx installable)
├── decompose-task/  # Break large tasks into atomic sub-tasks
├── diff-check/      # Author cleanup before commit/PR submit
├── market-research/ # Research products/competitors
└── spec-template/   # 9-section product spec pattern

agents/              # Shareable agent definitions (manual sync)
├── product.agent.md # Product designer: spec.md from idea
├── lead.agent.md    # Tech lead: plan.md + orchestration
├── engineer.agent.md# Dedicated implementation
└── reviewer.agent.md# Critical "grill me" review

prompts/             # Shareable prompts (manual sync)
├── new-project.prompt.md  # Start new project → @product
├── new-agent.prompt.md    # Create new agent → @lead
├── work-on-next.prompt.md # Next task → @lead
└── self-improve.prompt.md # Meta nudge for improvement

template/            # Skill template for creating new skills
└── SKILL.md
```

## Installation

### Skills (automatic via npx)

```bash
npx skills add b1tank/skills
```

This installs all skills from `skills/` to `~/.copilot/skills/`.

### Agents & Prompts (manual sync)

Use the sync script to copy agents and prompts to a target repo:

```bash
./sync.sh <target-repo-path>
```

Example:
```bash
./sync.sh ~/my-project
```

This copies:
- `agents/*.agent.md` → `<target>/.github/agents/`
- `prompts/*.prompt.md` → `<target>/.github/prompts/`

## Creating New Skills

1. Copy `template/SKILL.md` to `skills/<name>/SKILL.md`
2. Update the YAML frontmatter (name, description)
3. Write the skill instructions
4. Push to GitHub
5. Install: `npx skills add b1tank/skills`

## Reference

Based on [anthropics/skills](https://github.com/anthropics/skills/tree/main) structure.
