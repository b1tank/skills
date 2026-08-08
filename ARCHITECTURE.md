# Agent Architecture Reference

Conceptual reference for structuring **instructions**, **agents**, **skills**, and **prompts**.

For day-to-day usage and sync commands, see [README.md](README.md).

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
│    └── .github/              ← canonical in this repo               │
│        ├── agents/           (syncs to VS Code user-data)           │
│        ├── prompts/          (syncs to VS Code user-data)           │
│        ├── skills/           (repo-local skills)                    │
│        └── copilot-instructions.md (loaded when chatting here)      │
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
│    ├── agents/                   From ~/skills/.github/agents/      │
│    │   └── [synced + repo-specific agents]                          │
│    │                                                                │
│    ├── prompts/                  From ~/skills/.github/prompts/     │
│    │   └── [synced + repo-specific prompts]                         │
│    │                                                                │
│    └── skills/                   Repo-specific only                 │
│        └── [project-specific skills]                                │
└─────────────────────────────────────────────────────────────────────┘
```

**Sync strategy (high-level):**
- Bidirectional sync with VS Code user-data (`./sync.sh to-userdata` / `from-userdata`)
- Bidirectional sync with Codex skills (`./sync.sh to-codex` / `from-codex`)
- One-way copy into other repos (`./sync.sh to-repo <path>`)

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
| `product-designer` | Product Designer | Drafts `spec.md` from a one-liner idea; asks clarifying questions; uses `market-research` + `spec-template` |
| `planner` | Planner | Turns a work item into an ordered task breakdown; invokes `decompose-task` for large work |
| `lead` | Tech Lead | Orchestrates execution, delegates to engineer/reviewer, balances scope/risk |
| `engineer` | Software Engineer | Dedicated implementation; writes code and tests; follows commit discipline |
| `reviewer` | Code Reviewer | Critical review of diffs/commits/PRs; uses `diff-check` as a final sweep |
| `explainer` | Explainer | Educational agent that explains code changes; uses diagrams and visuals |
| `ui-tester` | UI Tester | Guided UI verification; produces manual verification steps |

**Typical flow (one of many):**
```
User request → @planner → @engineer → @reviewer
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

### Global Skills → `~/.copilot/skills/` (installed)

Skills useful across projects, installed via `npx skills add`:

| Skill | Description |
|-------|-------------|
| `decompose-task` | Break large task (>100 lines) into atomic sub-tasks |
| `diff-check` | Author's cleanup before submit (no debug code, secrets, redundant changes) |
| `market-research` | Research existing products/competitors; analyze features; identify gaps |
| `spec-template` | 9-section product spec pattern |
| `clone-with-hash` | Clone a repo into a unique `-<hash>` folder for isolated parallel work |

### Repo Agents → `.github/agents/` (canonical)

Agents that address common concerns. This document focuses on *roles and boundaries*; see [README.md](README.md) for the concrete inventory and sync commands.

### Repo Prompts → `.github/prompts/` (canonical)

Prompts are lightweight triggers that route work to the right agent (triage vs planning vs implementation). Avoid embedding repo-specific workflow assumptions in prompt content.

### Repo Skills → `.github/skills/`

In this repo, `.github/skills/` is the canonical location for skills you want available while working here.

To make skills globally available across all repos (outside of this repo), install them into `~/.copilot/skills/` via `npx skills add`.

---

## Prompts Detail

### Key Prompts

| Prompt | Purpose | Invokes |
|--------|---------|--------|
| `new-project` | Start new project from one-liner idea | `@product-designer` |
| `new-agent` | Create new agent (like hiring a team member) | `@lead` |
| `work-on-next` | Start next task — routes to triage, planning, or implementation | `@planner` / `@engineer` |
| `self-improve` | Meta nudge for agent/skill improvement | N/A |
| `create-pr` | Run diff-check, commit, push, create PR | N/A |
| `grill-me-for-pr` | Pre-PR readiness review | `@reviewer` |
| `sprint-in-yolo` | Execute full sprint autonomously | N/A |
| `continue-in-new` | Document state for session handoff | N/A |
| `verify-ux` | Launch app and verify UX | N/A |

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

## Skills Integration

**Skills workflow (automatic via npx):**
1. Develop skill in `.github/skills/<name>/SKILL.md`
2. Push to GitHub: `cd ~/skills && git add . && git commit && git push`
3. Others install: `npx skills add b1tank/skills`

**Agents/Prompts workflow (sync.sh):**
1. Develop in `.github/agents/` or `.github/prompts/`
2. Sync to VS Code user-data: `./sync.sh to-userdata --apply`
3. Or copy to another repo: `./sync.sh to-repo <path>`

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
| **Detailed specs** | `@product-designer` drafts spec.md; `spec-template` skill |
| **Use subagents** | `@lead` delegates to `@engineer` via subagent |
| **Explain the why** | Learning mode in instructions |
| **Visual presentations** | Learning mode: offer HTML presentations |
| **ASCII diagrams** | Learning mode: use diagrams for architecture |

---

## File Structure Template

```
~/skills/                    # Source repo (b1tank/skills)
├── README.md
├── ARCHITECTURE.md
├── sync.sh
├── .claude/hooks/           # Claude Code hooks
│   └── langfuse_hook.py     # Langfuse tracing
├── .github/
│   ├── copilot-instructions.md
│   ├── agents/
│   │   └── [agent-name].agent.md
│   ├── prompts/
│   │   └── [prompt-name].prompt.md
│   └── skills/
│       └── [skill-name]/SKILL.md
```

<other-repo>/.github/        # Per-repo (synced via ./sync.sh to-repo)
├── copilot-instructions.md  # Repo-wide rules + learning mode
├── agents/                  # Synced from ~/skills
├── prompts/                 # Synced from ~/skills
├── skills/                  # Repo-specific skills

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

---

## Cross-harness projection architecture


The repository stores semantic customizations once, then projects them into each harness's native format.

```text
                    ~/skills (Git, no secrets)
          skills   prompts   agents   instructions   MCP manifest
             \        |         |          |             /
                         ./setup.sh
                              |
      +-----------+-----------+-----------+-----------+
      |           |           |           |           |
   VS Code     Copilot      Claude      Codex      Pi/OpenCode
   native MD   native MD    command MD  agent TOML  adapters
```

## Design rules

1. `.github/` and `mcp/servers.json` are canonical; user-directory files are projections.
2. `~/.agents/skills` is the neutral shared skill root. Claude receives an additional projection because it uses its own user root.
3. A prompt remains a native slash command where supported and becomes an explicitly triggered skill elsewhere.
4. Agents are converted from VS Code `.agent.md` into the minimum native Claude, Codex, or OpenCode representation. Unsupported tool allowlists are omitted rather than mistranslated.
5. MCP is data, not copied client config. A secret-free manifest renders each native client's schema and a token-efficient MCPorter registry for Pi. Product-owned Pi adapters may expose the same MCP implementation as native Pi tools when richer lifecycle or image handling matters.
6. Installation is idempotent. Canonical links are left alone, collisions are backed up, and structured MCP files are merged.
7. Workspace configuration stays workspace-scoped. In particular, `.vscode/mcp.json` is never treated as global state.

See [the compatibility matrix](docs/agent-customization-compatibility.md) for concrete paths and caveats.
