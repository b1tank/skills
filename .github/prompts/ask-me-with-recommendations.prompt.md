---
name: ask-me-with-recommendations
description: Ask only the user decisions required to continue, with a clear recommendation and default for each.
---

Inspect the current task, repository instructions, existing evidence, and prior user answers. Identify only decisions that genuinely require user judgment before the next safe action.

Do not ask for information that can be derived from the repository, tools, documentation, environment, or prior conversation. Do not repeat answered questions, split one decision into several questions, ask broad preference surveys, or end with “anything else?” If no user input is required, say so and state the recommended next action instead of inventing questions.

For each required decision, provide:

1. **Question** — one concrete choice the user can answer directly.
2. **Recommendation** — the option you recommend.
3. **Why** — only the consequential tradeoff or blocker the choice resolves.
4. **Default** — what you will use if the user has no preference, when a safe default exists.

Merge dependent choices, order stop-now decisions first, and keep the list to the minimum that unlocks the work. Clearly distinguish required decisions from optional later preferences. Do not request credentials or secrets; ask the user to authenticate through the appropriate tool or approved mechanism when authorization is required.

Stop after the questions so the user can answer before irreversible, architectural, public, or high-cost work proceeds.
