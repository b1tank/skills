---
name: oss-feed-me
description: Find the highest-probability credible OSS contribution available now, or investigate a supplied symptom, issue, PR, branch, repository, or technical area.
argument-hint: "[repo(s), issue/PR URL, symptom, area, or goal]"
---

Help the user make a useful open source contribution today. Adapt to the invocation and current workspace instead of requiring a mode flag. If neither identifies a repository, ask for the minimum missing information.

## Infer the task

- No specific target: scout the current repository.
- One or more repositories: compare and rank opportunities across them.
- "New round" or a technical area: refresh tracker research and derive targeted probes from current source and recent changes.
- Symptom, reproduction, log, or screenshot: investigate whether it is new, known, fixed, duplicate, upstream, extension-specific, intended, or a feature request.
- Issue URL or number: assess reproduction, ownership, overlap, maintainer interest, and contribution readiness.
- PR, commit, fork, or compare URL: validate whether the proposed fix is correct, complete, and still needed.
- Several candidates: compare them before recommending one.
- Merged work: check release status, reporter confirmation, regressions, and sibling variants.

## Establish constraints

1. Read repository instructions, contribution and AI policies, issue/PR templates, approval gates, and validation requirements.
2. Inspect the user's relevant environment and legitimate test surfaces: OS, terminal, runtimes, installed release, local checkout, branch, remotes, and available providers or hardware. Do not expose credentials.
3. Distinguish installed release, local source, remote target branch, merged-but-unreleased fixes, and dirty worktrees. Use remote queries when possible; never pull, switch, overwrite, upgrade, alter credentials, or consume substantial paid quota without permission.

## Research and verify

1. Search open and closed issues, PRs, discussions, commits, release notes, assignments, in-progress labels, linked branches, forks, and compare views. Include gate-closed and superseded work when it reveals ownership or maintainer direction.
2. Read full threads and timelines. Prefer maintainer decisions, merged code, and reproduced evidence over titles, snippets, reactions, or speculation.
3. For existing opportunities, eliminate work that is owned, duplicated, already fixed, rejected, primarily subjective, too architectural for an initial contribution, or not reproducible in the user's environment.
4. For a reported symptom, confirm the shortest reproduction on the affected release and current target revision when practical. Test a negative control and separate core, extension, provider, OS, terminal, and upstream causes.
5. For proactive hunting, inspect recent source churn, bug fixes with narrow coverage, untested platform branches, and high-risk boundaries. Prefer targeted combinations over random fuzzing: cancellation, retries, timeouts, empty or partial events, lifecycle/reload, concurrency, limits, Unicode, filesystem behavior, networking, long sessions, and performance-sensitive loops.
6. Run only safe isolated probes. Use temporary files and configurations and clean them up. Ask first before destructive, expensive, credential-changing, user-data-changing, or paid tests.
7. Do not call an anomaly a new bug until it reproduces twice, has a negative control, has been searched by symptom and likely root cause, and has been checked against current source and history.
8. After technical confirmation, assess user significance separately: whether a supported or reasonably common workflow can reach it, whether users have observed it, likely prevalence and severity, available workarounds, and the cost imposed on maintainers. Label deliberately adversarial or synthetic probes as such.
9. Do not promote a finding to the public tracker merely because it is reproducible. Keep contrived, low-impact robustness cases as local notes unless they reveal meaningful risk, explain real reports, affect plausible configurations, or maintainers explicitly want hardening or fuzz findings.
10. When useful, test another contributor's or maintainer's branch under realistic conditions and report concise supporting or contradictory evidence.
11. Calibrate scouting against the repository's own successful history: inspect recent issue-to-merged-PR pairs in the relevant package or platform and note which problem shapes, evidence, patch sizes, and validation maintainers accepted quickly.

## Scout high-probability small fixes

Favor defects with a high diagnosis-to-diff ratio, especially when several signals align:

- an exact error, protocol sequence, or deterministic minimal reproduction points to one branch;
- one sibling model, provider, runtime, platform, terminal, or input shape works while another fails;
- current source contains a narrow hardcoded constant, allowlist, prefix, regex, switch case, feature gate, or missing option pass-through;
- upstream documentation or a canonical client changed and local metadata, routing, exports, or defaults are stale;
- user-facing examples, tutorials, templates, or SDK snippets still use deprecated imports, renamed methods, removed flags, stale commands, or superseded configuration;
- a value crosses a representation boundary incorrectly, such as string versus array, LF versus CRLF, visible width versus code-unit length, URL query versus fragment, or ambient credentials versus bearer tokens;
- Node versus compiled binary, npm versus registry metadata, or one OS/runtime exposes a parity gap;
- nearby code already implements the intended behavior for an analogous case, making the invariant and regression test clear;
- the fix is local to roughly one to three implementation files and fits an existing focused test suite without policy or architecture decisions.

Treat documentation and examples as executable user contracts: confirm the stale usage against current source and deprecation guidance, then run, compile, typecheck, lint, or build the narrowest relevant example or docs target. Prefer the smallest correction and avoid unrelated prose cleanup.

Do not equate a tiny diff with an easy contribution. Reject candidates whose expected behavior is subjective, whose reproduction is weak, or whose small change hides broad compatibility risk. Before taking a seemingly obvious fix, search issue comments, gate-closed PRs, fork branches, and compare links for an existing implementation. Validate or coordinate with its owner rather than recreating or repackaging it without consent and attribution.

## Rank for credible impact

Score candidates by demonstrated user pain, reachability through normal supported workflows, reproducibility, user/environment fit, maintainer acknowledgment, ownership risk, objective testability, implementation size, expected value, and probability of producing a useful contribution. Treat triage, reproduction, closure evidence, and fix validation as valid contributions—not only merged code.

Recommend one best task for today and at most two backups. Prefer small reliability, correctness, regression, or performance fixes with clear expected behavior over features, settings, broad refactors, taste-heavy UX work, or synthetic edge cases with no evidence of real-world impact. It is valid to report that no contribution is worth pursuing today.

## Prepare the next step

For a strong diagnosis:

- link the smallest relevant source range at an exact revision;
- explain the root invariant and outline a focused regression test;
- state investigation depth and unresolved uncertainty;
- check ownership again immediately before implementation;
- recommend adding evidence, coordinating, requesting approval, preparing a personal-fork compare branch, waiting, or stopping;
- treat a compare branch as a proposal and do not open a PR before required approval.

## Report

Lead with a verdict and confidence. For scouting, provide:

- **Best task today:** repository, candidate, why it fits, ownership/gate status, estimated scope, and one immediately executable first test with success/failure signals.
- **Backups:** at most two.
- **Proactive probes:** concrete source-motivated corner cases when tracker work is weak.
- **Avoid today:** tempting candidates rejected for ownership, duplication, scope, low confidence, contrived reachability, negligible impact, or lack of demonstrated user pain.

For a supplied target, report reproduction status, classification, strongest related artifacts and dispositions, source/release applicability, owner and competition risk, contribution gate, smallest useful next action, and proposed regression coverage.

## Hard stop before public actions

Never perform any public or remote write action without the user's explicit manual confirmation of that exact action immediately beforehand. This includes even emoji reactions, comments, reviews, issue or PR creation/editing/closing, labels, assignments, pushes, merges, and releases. General approval to investigate or contribute is not authorization to publish, and confirmation of one action does not authorize another.

Research, test, and draft locally first. Before every public action, show the exact target, operation, and content, then stop for confirmation. Keep eventual public text short, human-reviewed, evidence-backed, and compliant with disclosure rules.
