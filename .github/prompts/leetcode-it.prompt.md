---
name: leetcode-it
description: Identify a LeetCode problem from a number, title, URL, screenshot, or vague description and create a sourced statement, blank Python scaffold, and plain-assert Python tests without solving it.
---

Use the problem identifier or description supplied with the invocation. If none
is supplied, ask for a number, title, URL, screenshot, or description and stop.

## Repository scope

Always use `~/joy` as the repository for this workflow, regardless of the
invocation's current working directory. Resolve `~` to the user's home directory,
read that repository's instructions, inspect its worktree, and place the three
practice files in its existing topic-based layout. Do not create LeetCode files
or commits in the invocation repository. If `~/joy` is missing or is not a Git
repository, ask the user how to proceed rather than falling back elsewhere.
Run validation and any explicitly requested solution updates or commits in
`~/joy`; verify the Git repository root before staging or committing. Document
run commands from the `~/joy` repository root and clearly report that location.

Prioritize quick problem setup, not metadata research. Once the problem identity,
statement, examples, constraints, and interface are clear, stop source retrieval
and create the practice files.

1. Read repository instructions, inspect the worktree and existing problem
   layout, and preserve unrelated changes and existing solutions. Resolve the
   input to a canonical LeetCode number, title, and slug using official sources
   where possible. If a vague description has multiple plausible matches, show
   the likely candidates and ask for clarification before creating files.
2. Retrieve the problem statement with minimal source requests. Start with the
   supplied URL or screenshots; prefer official descriptions or public problem
   APIs when readily accessible. If blocked or incomplete, use an attributed
   public mirror rather than repeatedly trying official endpoints. Search only
   as necessary to identify the problem or recover its statement, examples,
   constraints, or class/method interface. Save optional metadata only if it is
   already present in supplied material or the responses used to obtain the
   problem. Do not make additional searches, fetches, or API calls for metadata
   such as difficulty, topic tags, companies, hints, statistics, or similar
   questions, including locked fields. Do not cross-check or enrich optional
   metadata with extra sources; omit missing fields without a missing-metadata
   audit. Do not bypass authentication, paywalls, or anti-bot protections, or
   change tool/security configuration just to fetch a page. Never invent fields
   or persist personal account state, credentials, or private browser output.
3. Create exactly three practice files in a location consistent with the
   repository. Include the problem number and slug in filenames, but use valid
   Python module names for both Python files so tests can use a simple sibling
   import (for example, `from leetcode_123_problem_slug import Solution`). Avoid
   dynamic import machinery and numeric-leading or hyphenated Python filenames.
   Do not overwrite existing practice work without confirmation. Do not add a
   generator, dependencies, or a solution unless separately requested.
   - **Problem Markdown:** format the full statement, examples, constraints,
     any supplied follow-up, canonical reference link, language, class/method
     signature, and input/output contract. Optionally save metadata already
     encountered while obtaining the problem, such as difficulty, topic tags,
     acceptance/submission statistics, hints, companies, or similar questions;
     do not retrieve anything extra for it. Attribute saved metadata, label
     dynamic values with their capture date when known, and distinguish
     third-party claims or screenshot snapshots from live official metadata.
     Omit absent optional fields; do not add unavailable-field tables or long
     source-availability reports. Never guess. Keep optional hints and spoilers
     collapsed; do not include editorials or algorithms. Keep source notes brief,
     attribute fallback sources, and warn if a reference contains solutions.
   - **Python scaffold:** match LeetCode's class, method names, argument order,
     annotations, and any required helper structures as closely as possible.
     Use the requested typing style (default to modern `list[int]` when
     applicable), add only necessary imports, and record the canonical link.
     Leave each exercise method body as `pass`. Add an
     `if __name__ == "__main__":` block containing only `pass` so the learner
     can write their own experiments. Do not insert example calls or hints.
   - **Python tests:** keep them interview-simple: a direct sibling import,
     a `main()` function, a plain list of input/expected-output tuples, a loop
     that calls `Solution` and compares the result with a plain `assert`, and
     `if __name__ == "__main__": main()`. Each tuple contains only the method
     inputs and expected output (for example, `(nums, k, expected)`). Describe
     cases with comments, never description keys, name strings, or extra label
     fields. Keep the loop easy to write under interview pressure; a short
     assertion message is enough.
     Do not use `unittest`, `pytest`, test classes, dynamic imports, or another
     test framework. A final passed-case count is enough; no custom runner is
     needed. Include official examples plus a small set of nonredundant common
     and edge cases: minimum sizes, boundary parameters, duplicates, ordering,
     signs/zero, value limits, and representative maximum-size inputs where
     relevant and practical. For
     design problems, test operation sequences and state transitions. Include
     expected outputs, isolate mutable inputs, and do not assume immutability
     or behavior outside the stated contract. Do not embed a reference solution
     or skip assertions just because the scaffold is blank.
4. Add exact commands to the Markdown for running the scaffold and test file
   from the repository root, plus the Python/runtime requirement and a concise
   coverage summary. Explain that tests intentionally fail until implementation
   and that representative coverage is not exhaustive judge coverage.
5. Verify Python syntax, the simple sibling import, and the documented direct
   execution commands. Run tests with normal Python (not `python -O`, which
   disables assertions) and confirm the blank scaffold produces an assertion
   failure, not an import error. Plain assertions stop at the first failing case.
   Independently check expected outputs; any temporary reference used for
   validation must remain outside the saved practice files. Confirm all
   exercise bodies and the scaffold's main block
   remain `pass`, then review the diff for unrelated changes and spoilers.
6. Briefly report the resolved problem, three file paths, run commands, and
   verification results. Mention source gaps only if they affect the statement
   or practice contract, not missing optional metadata. Clearly distinguish
   expected unsolved-test failures from setup defects. Do not commit or push
   practice files unless explicitly requested.
