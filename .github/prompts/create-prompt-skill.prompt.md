---
name: create-prompt-skill
description: Execute a requested workflow now, turn it into a named reusable prompt skill, and publish it across all configured agent harnesses.
argument-hint: <workflow to execute and save>
---

## Requested workflow

Use the workflow supplied with the invocation.

Treat the requested workflow above as both:

1. a task to execute in the current repository; and
2. a concrete example from which to create a reusable prompt skill.

## Workflow

1. Read `~/skills/BOOTSTRAP.md` and inspect the existing prompts in
   `~/skills/.github/prompts/` before making changes.
2. Execute the requested task completely in the current repository. Respect
   that repository's instructions and do not broaden destructive or external
   actions beyond the user's request.
3. Derive a concise, verb-led, lowercase hyphenated name, at most 63
   characters. Prefer the reusable intent over literal wording. If the name
   already exists, update it only when the new workflow is clearly the same;
   otherwise choose a distinct name.
4. Create `~/skills/.github/prompts/<name>.prompt.md` with only `name` and
   `description` in its YAML frontmatter. Generalize current repository names,
   PR numbers, paths, branches, and incidental details. Preserve safeguards,
   verification, and completion criteria. Write it as an actionable prompt,
   not as documentation about the original request.
5. Do not persist credentials, private output, or instructions that are useful
   only once. If the request contains secrets, redact them. If it cannot be
   made safely reusable, complete the task but explain why no prompt was saved.
6. In `~/skills`, run `./setup.sh generate`, inspect the generated command
   and prompt-skill projection, run `npm test`, then run
   `./setup.sh bootstrap` and `./setup.sh validate`.
7. Commit only the intended `b1tank/skills` source changes and generated files
   tracked by the repository, then push the current branch. Preserve unrelated
   worktree changes.
8. Report the completed task, chosen slash command, source file, validation,
   commit, and push result.

## Polished example

Invocation:

```text
/create-prompt-skill pull PR review comments, audit whether each is valid, and address the valid ones
```

Derived command: `/auto-address`

Representative reusable prompt:

```markdown
---
name: auto-address
description: Review the current pull request's feedback, validate every actionable comment, and address the valid findings.
---

Pull all review comments and unresolved threads for the current branch's pull
request. For each comment, inspect the relevant code and determine whether the
finding is still applicable and technically valid.

- Address valid findings with focused changes that follow repository
  instructions.
- Do not implement invalid, obsolete, duplicate, or purely speculative
  suggestions; record a concise reason for each one skipped.
- Run the relevant tests and diff checks after editing.
- Re-read the review threads and summarize each finding as addressed, already
  resolved, or declined with rationale.

Do not resolve or reply to remote review threads unless the user explicitly
authorized those external actions.
```

Use the example as a quality bar and naming reference, not as a fixed template.
