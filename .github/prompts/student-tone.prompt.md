---
name: student-tone
description: Explain a technical topic briefly in a clear student-friendly tone using plain language and concrete examples.
argument-hint: "<topic or code to explain>"
---

Explain the requested topic as if the reader is a new intern who understands basic software concepts but does not yet know this project.

- Start with the purpose: what the code or change is trying to accomplish.
- Describe the current flow before explaining the proposed change.
- Use plain language, short sentences, and one small example or analogy when helpful.
- Define unavoidable project terms the first time they appear.
- Avoid unexplained acronyms, dense implementation details, and long code excerpts.
- Clearly separate what already exists, what would change, and what would remain unchanged.
- Call out the main risk, required verification, and rough effort when relevant.
- Keep the answer concise, but do not omit an important limitation or uncertainty.

If the repository source is available, inspect the relevant code before explaining it. Distinguish confirmed behavior from assumptions, and say when live behavior was not verified.
