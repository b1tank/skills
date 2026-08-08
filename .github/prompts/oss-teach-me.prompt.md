---
name: oss-teach-me
description: Trace how external contributors build credibility in an open source repository and extract evidence-backed practices to learn from.
---

Study public contribution history to teach the user how external contributors become useful and trusted over time. Accept a repository, an account handle or profile URL plus repository, several contributors to compare, or infer the repository from the current workspace. If a handle is supplied without an unambiguous repository, ask for it. If only a repository is supplied, identify a small evidence-rich set of recent external contributors before tracing them.

## Establish scope and safeguards

1. Record the repository, target contributors, observation cutoff date, and current revision when relevant.
2. Read the repository's contribution guide, AI policy, issue and PR templates, submission gates, and current instructions. Inspect historical versions when a rule change affected a contributor's path.
3. Use only public repository activity needed to understand contribution behavior. Do not collect or report private data, credentials, email addresses, numeric account IDs, unrelated personal history, or speculative personality judgments.
4. Distinguish external contributors from organization members and collaborators using public author associations and repository evidence. State when status is ambiguous or changed over time.

## Build a reliable chronology

1. Search authored and involved issues, PRs, discussions, commits, reviews, review comments, ordinary comments, timelines, compare branches, and contributor-approval records. Include open, merged, rejected, superseded, auto-closed, and rewritten work.
2. Do not treat an old issue's creation date as the contributor's first appearance merely because they commented later. Collect interaction timestamps and sort the contributor's actual actions chronologically.
3. Read full threads and review conversations for the strongest milestones. Prefer exact comment, review, commit, and PR links over search snippets or aggregate counts.
4. Verify counts and dates with paginated queries where practical. Explain API caps, renamed repositories, dynamic author-association labels, or other limitations that could distort the record.
5. Separate facts from interpretation. Public maintainer invitations, delegation, merge decisions, and approval changes are credibility signals; they do not reveal private opinions or guarantee future acceptance.

## Trace the contribution path

Identify evidence for these phases when present, without forcing the story into a template:

- first appearance and quality of the initial report or proposal;
- early process mistakes, auto-closures, rejected designs, or maintainer corrections;
- adaptation to repository gates, scope, style, and ownership expectations;
- reproduction, triage, source investigation, branch validation, or support work for other users;
- issue-first proposals, exact source snippets, personal-fork compare branches, and explicit validation;
- first approval and first merged changes;
- growth from small fixes into deeper or cross-cutting work;
- maintainer requests, delegated investigations, implementation discretion, or invitations;
- post-merge support, regression follow-up, closure evidence, and coordination with other contributors;
- development of a recognizable technical niche.

Pay special attention to behavior that reduces maintainer workload: stating confidence, asking for missing evidence, avoiding duplicate ownership, narrowing scope, preserving attribution, accepting rejection without entitlement, testing others' branches, and withdrawing fixes that are no longer needed.

## Repository-wide mode

When no contributor is specified:

1. Find recent external contributors with both substantive public interaction and accepted work; do not rank solely by commit count.
2. Exclude or clearly separate current members and collaborators from ordinary external-contributor paths.
3. Select at most five contributors representing distinct useful patterns, such as triage, focused regression fixes, domain specialization, realistic validation, or long-term follow-through.
4. Deeply verify the strongest examples instead of producing a shallow leaderboard.

## Report

Lead with a concise summary and research cutoff. For each contributor provide:

- role or contribution niche;
- chronological milestones with direct evidence links;
- corrections or setbacks and how they responded;
- strongest public signals of increasing responsibility;
- practices worth copying and cautions against overgeneralizing;
- verified activity counts only when they add context.

End with:

- shared lessons across contributors;
- repository-specific contribution norms;
- a practical playbook the user can apply;
- explicit limitations and facts that cannot be inferred from public data.

Keep the prose technical and respectful. Do not turn the report into personal ranking, advocacy, or a claim that maintainers owe similar treatment to anyone else.

## Hard stop before public actions

Remain read-only. Never react, follow, post, comment, review, open or edit issues or PRs, label, assign, push, merge, or perform any other public or remote write without the user's explicit manual confirmation of that exact action immediately beforehand. If a public action could help, draft it locally, show the exact target and content, and stop for confirmation.
