# Agent Architecture Reference

The "golden bible" for setting up AI agent architecture in any repository.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GLOBAL (all repos)                          │
├─────────────────────────────────────────────────────────────────────┤
│  ~/.copilot/skills/          Installed via `npx skills add`         │
│    ├── skill-creator/        (anthropics/skills)                    │
│    └── [your skills]         (your-org/skills) - auto-installed     │
│                                                                     │
│  ~/skills/                   Version-controlled source repo         │
│    ├── skills/               ← installed via npx skills add         │
│    │   ├── decompose-task/SKILL.md                                  │
│    │   ├── diff-check/SKILL.md                                      │
│    │   └── [other skills]                                           │
│    │                                                                │
│    ├── agents/               ← manually sync/copy to repos          │
│    │   ├── product.agent.md                                         │
│    │   ├── lead.agent.md                                            │
│    │   ├── engineer.agent.md                                        │
│    │   └── reviewer.agent.md                                        │
│    │                                                                │
│    └── prompts/              ← manually sync/copy to repos          │
│        ├── new-project.prompt.md                                    │
│        ├── new-agent.prompt.md                                      │
│        ├── work-on-next.prompt.md                                   │
│        └── self-improve.prompt.md                                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                        (sync/copy shareable items)
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      REPO-SPECIFIC                                  │
├─────────────────────────────────────────────────────────────────────┤
│  .github/                                                           │
│    ├── copilot-instructions.md   Repo-wide rules (always loaded)    │
│                                                                     │
│  AGENTS.md (root) → .github/copilot-instructions.md                 │
│  .claude/CLAUDE.md → ../.github/copilot-instructions.md             │
│    │                                                                │
│    ├── agents/                   From ~/skills/agents/ + local      │
│    │   └── [synced + repo-specific agents]                          │
│    │                                                                │
│    ├── prompts/                  From ~/skills/prompts/ + local     │
│    │   └── [synced + repo-specific prompts]                         │
│    │                                                                │
│    └── skills/                   Repo-specific only                 │
│        └── [project-specific skills]                                │
└─────────────────────────────────────────────────────────────────────┘
```

**Sync strategy:**
- Skills: `npx skills add your-org/skills` (automatic)
- Agents/Prompts: `./sync.sh <target-repo>` copies from `~/skills/` to repo's `.github/`

---

## Conceptual Framework

| Concept | Definition | Autonomy | Location | Example |
|---------|-----------|----------|----------|---------|
| **Instructions** | Repo-wide rules all agents/skills follow | N/A | `.github/copilot-instructions.md` | Project structure, commit policy, learning mode |
| **Agent** | Autonomous role with decision-making; analogous to team member | High | `.github/agents/*.agent.md` | `@lead`, `@engineer`, `@reviewer` |
| **Skill** | Reusable procedure/knowledge; no autonomy | None | `~/.copilot/skills/` or `.github/skills/` | `decompose-task`, `diff-check` |
| **Prompt** | Quick trigger/nudge to invoke agent or shift behavior | N/A | `.github/prompts/*.prompt.md` | `/work-on-next` |

**Key distinctions:**
- **Agent vs Skill**: Agents make decisions and can delegate; skills execute procedures and return results
- **Global vs Repo Skill**: Shareable skills go to `~/skills/` (published via your-org/skills); repo-specific stay in `.github/skills/`
- **Prompt**: User-facing trigger, not an agent itself

---

## Agent Roles (Team Analogy)

| Agent | Role | Responsibilities |
|-------|------|------------------|
| `product` | Product Designer | Drafts spec.md from user's one-liner idea; asks clarifying questions; researches market; follows spec template pattern |
| `lead` | Tech Lead | Generates plan.md from spec.md; orchestrates work; delegates to engineer/reviewer; makes architecture decisions; handles simple tasks directly |
| `engineer` | Software Engineer | Dedicated implementation; writes code, tests, commits; invoked by lead or manually in separate window |
| `reviewer` | Code Reviewer | Critical review of diffs/commits/PRs; "grill me" mindset; provides critical + nitpick feedback; scores quality |

**Project lifecycle flow:**
```
User one-liner → @product (spec.md) → @lead (plan.md) → @engineer (impl) → @reviewer (review)
```

**Why both lead and engineer?**
- Lead orchestrates and can do simple impl; engineer is dedicated implementer
- Enables parallel work: trigger different engineers in separate agent windows
- Cleaner separation: lead focuses on planning/coordination, engineer on execution

**Reviewer modes:**
- **Single-person**: Review local diffs/commits (no PR needed)
- **Multi-person**: Given a PR URL, checkout branch and review

---

## Skills Distribution

### Shareable Skills → `~/skills/skills/`

Skills useful across projects, installed via `npx skills add`:

| Skill | Description |
|-------|-------------|
| `decompose-task` | Break large task (>100 lines) into atomic sub-tasks |
| `diff-check` | Author's cleanup before submit (no debug code, secrets, redundant changes) |
| `market-research` | Research existing products/competitors; analyze features; identify gaps |
| `spec-template` | 9-section product spec pattern |

### Shareable Agents → `~/skills/agents/`

Agents that address common concerns, synced via `./sync.sh`:

| Agent | Description |
|-------|-------------|
| `product` | Product designer: spec.md from idea |
| `lead` | Tech lead: plan.md + orchestration |
| `engineer` | Dedicated implementation; parallel windows support |
| `reviewer` | Critical "grill me" review for commits/PRs |

### Shareable Prompts → `~/skills/prompts/`

Prompts that trigger common workflows:

| Prompt | Purpose | Invokes |
|--------|---------|---------|
| `new-project` | Start new project from one-liner idea | `@product` |
| `new-agent` | Create new agent (like hiring a team member) | `@lead` |
| `work-on-next` | Start next atomic task from plan | `@lead` |
| `self-improve` | Meta instruction for agent/skill improvement | N/A |

### Repo-Specific Skills → `.github/skills/`

Skills specific to a single project only. Examples:
- `tauri-contract` — TS ⇄ Rust contract sync
- `db-schema` — Database migration procedures
- `api-versioning` — API deprecation workflow

---

## Prompts Detail

### `new-project` Prompt

Start a new project from a one-liner idea.

**Flow:**
1. User provides one-liner (e.g., "A lightweight screen recorder")
2. @product asks clarifying questions
3. Uses `market-research` skill to analyze competitors
4. Drafts spec.md using `spec-template` skill
5. Iterates with user until approved

### `new-agent` Prompt

Create a new agent role (hiring analogy).

**Flow:**
1. User describes needed role (e.g., "I need a devops agent")
2. @lead analyzes responsibilities
3. Identifies skills the agent should use
4. Determines decision boundaries
5. Drafts agent file following patterns
6. Suggests placement (shareable vs repo-specific)
7. Creates after user confirmation

---

## Instructions Scope

**`copilot-instructions.md`** (symlinked as `AGENTS.md` and `CLAUDE.md`):
- Project structure & module organization
- Build/test commands
- Coding principles
- Cross-layer contract rules (reference skills for details)
- State machine policy
- Testing guidelines
- Work categories & commit message format
- Commit and push policy (reference `diff-check` skill)
- Task decomposition policy (reference `decompose-task` skill)
- **Learning mode**

### Learning Mode

Add to instructions—applies to all agents:

```markdown
## Learning Mode

When explaining code or changes:
- Explain the *why* behind changes, not just the what
- Use ASCII diagrams to illustrate architecture, data flow, protocols
- Offer to generate visual HTML presentations for complex concepts
- When reviewing unfamiliar code, summarize structure before diving in
- Ask follow-up questions to fill knowledge gaps
```

---

## Decision Log (Rationale)

| Decision | Rationale |
|----------|-----------|
| Product = agent | Autonomous: asks questions, researches, drafts spec.md |
| Lead generates plan.md | Natural flow: spec → plan → impl |
| Market research = skill | Reusable procedure; product agent calls it |
| Spec template = skill | 9-section pattern reusable across projects |
| Reviewer = agent | Autonomous critical judgment; "grill me" mindset |
| diff-check = skill | Procedural cleanup by author; no autonomous decisions |
| decompose-task = skill | No autonomy; returns analysis to caller |
| Both lead + engineer | Lead orchestrates; engineer for dedicated impl + parallel windows |
| Learning mode in instructions | Behavioral preference applies to all agents |
| Shareable skills in ~/skills/skills/ | Version control + `npx skills add` distribution |
| Shareable agents in ~/skills/agents/ | Version control; manual sync to repos |
| Shareable prompts in ~/skills/prompts/ | Version control; manual sync to repos |
| Symlink AGENTS.md/CLAUDE.md | Single source of truth; works for all AI tools |

---

## Skills.sh Integration

**Skills workflow (automatic via npx):**
1. Develop skill in `~/skills/skills/<name>/SKILL.md`
2. Push to GitHub: `cd ~/skills && git add . && git commit && git push`
3. Others install: `npx skills add your-org/skills`

**Agents/Prompts workflow (manual sync):**
1. Develop in `~/skills/agents/` or `~/skills/prompts/`
2. Push to GitHub for version control
3. Run sync script: `./sync.sh <target-repo>`

**Skill format** (per anthropics/skills spec):
```markdown
---
name: skill-name
description: Clear description of what this skill does and when to use it
---

# Skill Name

[Instructions for Claude]

## Process
1. Step one
2. Step two

## Output Format
[Expected output structure]
```

**Reference:** https://github.com/anthropics/skills/tree/main

---

## Claude Tips Coverage

How this architecture addresses [claude-tips](https://x.com/bcherny/status/2017742741636321619) recommendations:

| Tip | Implementation |
|-----|----------------|
| **Parallel worktrees** | `@engineer` agent runs in separate windows |
| **Plan mode** | `decompose-task` skill; `@lead` orchestrates |
| **Invest in CLAUDE.md** | Symlink to `copilot-instructions.md` |
| **Create skills** | `~/skills/` repo with skills.sh integration |
| **Grill me** | `@reviewer` agent with "grill me" mindset |
| **Detailed specs** | `@product` drafts spec.md; `spec-template` skill |
| **Use subagents** | `@lead` delegates to `@engineer` via subagent |
| **Explain the why** | Learning mode in instructions |
| **Visual presentations** | Learning mode: offer HTML presentations |
| **ASCII diagrams** | Learning mode: use diagrams for architecture |

---

## File Structure Template

```
~/skills/                    # Source repo (your-org/skills)
├── README.md
├── sync.sh
├── skills/
│   └── [skill-name]/SKILL.md
├── agents/
│   └── [agent-name].agent.md
├── prompts/
│   └── [prompt-name].prompt.md
└── template/
    └── SKILL.md

.github/                     # Per-repo
├── copilot-instructions.md  # Repo-wide rules + learning mode
├── README.md                # How to use agents, skills, prompts

AGENTS.md (root)             # → symlink to .github/copilot-instructions.md
.claude/CLAUDE.md            # → symlink to ../.github/copilot-instructions.md
├── agents/
│   └── [synced + repo-specific].agent.md
├── prompts/
│   └── [synced + repo-specific].prompt.md
└── skills/
    └── [repo-specific skills only]
```

---

## Setting Up a New Repo

1. **Install global skills**: `npx skills add your-org/skills`
2. **Sync agents/prompts**: `cd ~/skills && ./sync.sh <new-repo>`
3. **Create symlinks**:
   ```bash
   # From repo root
   ln -s .github/copilot-instructions.md AGENTS.md
   mkdir -p .claude && ln -s ../.github/copilot-instructions.md .claude/CLAUDE.md
   ```
4. **Customize instructions**: Edit `copilot-instructions.md` for project-specific rules
5. **Add repo-specific skills**: Create in `.github/skills/` as needed
