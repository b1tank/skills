---
name: scaffold-leetcode
description: Identify a LeetCode problem from a number, title, URL, screenshot, or vague description and create a sourced statement, blank Python scaffold, and focused tests without solving it.
---

Use the problem identifier or description supplied with the invocation. If none
is supplied, ask for a number, title, URL, screenshot, or description and stop.

1. Read repository instructions, inspect the worktree and existing problem
   layout, and preserve unrelated changes and existing solutions. Resolve the
   input to a canonical LeetCode number, title, and slug using official sources
   where possible. If a vague description has multiple plausible matches, show
   the likely candidates and ask for clarification before creating files.
2. Retrieve the statement and metadata from the official description page or
   public problem API when available. Use supplied screenshots and clearly
   attributed public mirrors as fallbacks. Do not bypass authentication,
   paywalls, or anti-bot protections, or change tool/security configuration just
   to fetch the page. Never invent unavailable fields or persist personal
   account state, credentials, or private browser output.
3. Create exactly three practice files in a location consistent with the
   repository. Reuse its naming convention, including the problem number and
   slug; choose an importable test filename. Do not overwrite existing practice
   work without confirmation. Do not add a generator, dependencies, or a
   solution unless separately requested.
   - **Problem Markdown:** format the full statement, examples, constraints,
     follow-up, canonical reference link, difficulty, topic tags, language,
     class/method signature, and input/output contract. Include other metadata
     actually available, such as acceptance/submission statistics, hints,
     company tags, and similar-question links. Label dynamic values with their
     source and capture date when known; distinguish screenshot snapshots and
     third-party lists from live official metadata. Mark relevant inaccessible
     or premium-only fields as unavailable, rather than guessing. Keep optional
     hints and spoilers collapsed; do not include editorials or algorithms.
     Attribute fallback sources and warn if a reference contains solutions.
   - **Python scaffold:** match LeetCode's class, method names, argument order,
     annotations, and any required helper structures as closely as possible.
     Use the requested typing style (default to modern `list[int]` when
     applicable), add only necessary imports, and record the canonical link.
     Leave each exercise method body as `pass`. Add an
     `if __name__ == "__main__":` block containing only `pass` so the learner
     can write their own experiments. Do not insert example calls or hints.
   - **Python tests:** use the repository's test framework, or standard-library
     `unittest` if none exists. Load the scaffold robustly even when its filename
     contains a numeric prefix or hyphens. Include official examples plus a
     small, named set of nonredundant common and edge cases: minimum sizes,
     boundary parameters, duplicates, ordering, signs/zero, value limits, and
     representative maximum-size inputs where relevant and practical. For
     design problems, test operation sequences and state transitions. Include
     expected outputs, isolate mutable inputs, and do not assume immutability
     or behavior outside the stated contract. Do not embed a reference solution
     or skip assertions just because the scaffold is blank.
4. Add exact commands to the Markdown for running the scaffold and test file
   from the repository root, plus the Python/runtime requirement and a concise
   coverage summary. Explain that tests intentionally fail until implementation
   and that representative coverage is not exhaustive judge coverage.
5. Verify Python syntax, module loading, test discovery, and the documented
   commands. Run the tests and confirm the blank scaffold produces assertion
   failures, not import or harness errors. Independently check expected outputs;
   any temporary reference used for validation must remain outside the saved
   practice files. Confirm all exercise bodies and the scaffold's main block
   remain `pass`, then review the diff for unrelated changes and spoilers.
6. Report the resolved problem, three file paths, run commands, source gaps,
   and verification results. Clearly distinguish expected unsolved-test
   failures from setup defects. Do not commit or push practice files unless
   explicitly requested.
