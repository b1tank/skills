---
name: leetcode-it
description: Identify a LeetCode problem from a number, title, URL, screenshot, or vague description and create a sourced statement, blank Python scaffold, and plain-assert Python tests without solving it.
---

Use the problem identifier or description supplied with the invocation. If none
is supplied, ask for a number, title, URL, screenshot, or description and stop.

1. Read repository instructions, inspect the worktree and existing problem
   layout, and preserve unrelated changes and existing solutions. Resolve the
   input to a canonical LeetCode number, title, and slug using official sources
   where possible. If a vague description has multiple plausible matches, show
   the likely candidates and ask for clarification before creating files.
2. Retrieve the statement and metadata from the official description page or
   public problem API when available. If a problem, company tags, hints, or
   other metadata are premium-locked or inaccessible, actively web-search for
   the missing information on other public sites; do not stop at the lock icon
   or merely label it unavailable. Use supplied screenshots and attributed
   public mirrors as fallbacks. Verify the problem identity and distinguish
   third-party claims from current official metadata. Only mark a field
   unavailable after a reasonable public-source search finds nothing reliable.
   Do not bypass authentication, paywalls, or anti-bot protections, or change
   tool/security configuration just to fetch a page. Never invent fields or
   persist personal account state, credentials, or private browser output.
3. Create exactly three practice files in a location consistent with the
   repository. Include the problem number and slug in filenames, but use valid
   Python module names for both Python files so tests can use a simple sibling
   import (for example, `from leetcode_123_problem_slug import Solution`). Avoid
   dynamic import machinery and numeric-leading or hyphenated Python filenames.
   Do not overwrite existing practice work without confirmation. Do not add a
   generator, dependencies, or a solution unless separately requested.
   - **Problem Markdown:** format the full statement, examples, constraints,
     follow-up, canonical reference link, difficulty, topic tags, language,
     class/method signature, and input/output contract. Include other metadata
     actually available, such as acceptance/submission statistics, hints,
     company tags, and similar-question links. Label dynamic values with their
     source and capture date when known; distinguish screenshot snapshots and
     third-party lists from live official metadata. For locked fields, include
     reliable public-source findings with attribution; only mark them unavailable
     if the fallback search was unsuccessful. Never guess. Keep optional
     hints and spoilers collapsed; do not include editorials or algorithms.
     Attribute fallback sources and warn if a reference contains solutions.
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
6. Report the resolved problem, three file paths, run commands, source gaps,
   and verification results. Clearly distinguish expected unsolved-test
   failures from setup defects. Do not commit or push practice files unless
   explicitly requested.
