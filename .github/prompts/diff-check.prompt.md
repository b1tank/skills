---
description: Reusable code-quality checklist for diffs. Covers cleanup, security, modularity, test gaps, doc gaps, and commit hygiene. Used by engineers before committing and by reviewers during pre-PR readiness analysis.
argument-hint: "[diff target or review focus]"
---

# Diff Check

Reusable quality sweep for any changeset — staged files, branch diff, or PR patch.

## When to Use

- Before any `git commit`
- Before marking a PR ready for review
- As the first pass in a pre-PR readiness review
- After implementing changes, before requesting review

## Checklist

### 1. Scope & Focus
- [ ] Changes are within scope of the task/PR
- [ ] No redundant or unnecessary code changes
- [ ] No unrelated formatting or whitespace-only changes

### 2. Code Cleanup
- [ ] No debugging code left in (console.log, print, dbg!, etc.)
- [ ] No testing stubs or mock data in production code
- [ ] No commented-out code blocks (unless intentionally preserved)
- [ ] No dead code (unused imports, unreachable branches, orphaned helpers)
- [ ] No leftover TODOs that should be resolved before merge

### 3. Security
- [ ] No secrets, API keys, or credentials exposed
- [ ] No hardcoded local file paths (e.g., /home/user1/...)
- [ ] No sensitive information in comments or logs

### 4. Consistency & Naming
- [ ] Code follows project lint/format rules
- [ ] Naming conventions consistent with surrounding code
- [ ] Import statements are organized

### 5. Modularity & Structure
- [ ] No functions exceeding ~50 LOC — suggest extraction
- [ ] No god files with mixed concerns — suggest splits
- [ ] New abstractions are justified (not over-engineered)

### 6. Test Coverage
- [ ] New logic has corresponding tests (or a justification why not)
- [ ] Edge cases covered for non-trivial branching
- [ ] Tests actually run and pass (not just written — execute them)
- [ ] For bug fixes: regression test exists that would fail without the fix
- [ ] For refactors: existing test suite passes without modification (or changes are justified)
- [ ] No test-only code leaking into production paths
- [ ] UI changes have visual verification (manual prompt or Playwright snapshot)

### 7. Documentation
- [ ] Public API changes have doc updates
- [ ] README updated if user-facing behavior changed
- [ ] Non-obvious logic has inline comments

### 8. Commit Hygiene
- [ ] Diff could ship as-is (or note if it should be split into smaller PRs/commits)
- [ ] Commit messages are clear and follow project conventions

### 9. Branch Health (PR only)
- [ ] Synced with main/target branch
- [ ] No merge conflicts
- [ ] CI checks pass (if applicable)

### 10. Plan Alignment
- [ ] Relevant checkboxes in plan.md are marked complete (if applicable)

## Process

1. Determine changeset: staged files, `git diff <target>...HEAD`, or provided patch
2. Walk through all checklist sections above
3. Report issues with file:line references and recommended fixes
4. Do NOT make changes automatically — report for human confirmation

## Output Format

```
[DIFF CHECK COMPLETE]

Files reviewed: [N]
Issues found: [M]

Critical:
- [file:line] [issue description]

Warnings:
- [file:line] [issue description]

Cleanup:
- [file:line] [issue description]

Modularity:
- [file:line] [suggestion]

Test Gaps:
- [file] [what's missing]

Doc Gaps:
- [file] [what needs updating]

Commit Hygiene:
- [recommendation]

Status: [READY / NEEDS FIXES]
```
