---
name: polish-body
description: Rewrite and publish a clear, concise body for a GitHub pull request, issue, or discussion.
---

Polish the body of the requested GitHub artifact. Support pull requests, issues,
and discussions on `github.com`. If the target is another artifact type, clarify
the scope before editing it.

- Resolve the target from an explicit URL or number. Otherwise, use the current
  branch's pull request.
- Read repository instructions, the current title and body, relevant comments,
  and the source material needed to verify every claim. For a pull request,
  inspect the full branch diff, commits, validation results, base, head, and
  draft state.
- Create a body when none exists; otherwise rewrite the existing body.
- Lead with the purpose and actual behavior change. Use short sentences,
  compact bullets, and small tables only when they improve scanning.
- Remove repetition, implementation diaries, stale status, marketing language,
  and unsupported claims. A reviewer should understand the scope quickly.
- Preserve required templates, checklists, attribution, issue links, security
  notes, compatibility limitations, and meaningful validation or coverage gaps.
- Keep technical names and test results exact. Clearly distinguish verified
  behavior from expected behavior.
- Do not change code, title, labels, assignees, milestone, draft/open state, or
  review-thread state unless explicitly requested.

Write the proposed body to a temporary file, publish it with the appropriate
GitHub command, then re-read the remote artifact and verify its identity and
final body. Report the artifact URL and a concise summary of what changed.
