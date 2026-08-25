---
name: de-ai
description: Remove generic AI-writing habits from prose while preserving its meaning, clarity, and the author's individual voice.
---

Revise the requested prose so it reads like the author's own natural writing
rather than generic AI-polished text. Work only on the text or files the user
identifies. If no text or scope is provided, ask what should be revised instead
of guessing.

- Preserve every factual claim, opinion, example, qualification, link, and
  technical term. Do not add ideas, invent personal details, or change meaning.
- Remove canned transitions, inflated phrasing, repetitive summaries, excessive
  signposting, stacked rhetorical lists, and other patterns that make the prose
  feel templated.
- Avoid em dashes. Prefer a period, comma, colon, or parentheses according to
  the sentence. Use a hyphen only when normal grammar or a compound word calls
  for one.
- Keep deliberate informality, uneven rhythm, humor, emphasis, and
  author-specific expressions when they remain clear.
- Do not manufacture authenticity by adding slang, mistakes, fragments, or
  unsupported anecdotes. Do not make clear prose worse merely to make it less
  polished.
- Leave code, commands, frontmatter values, citations, URLs, and other
  non-prose content unchanged unless the user explicitly includes them.
- Make the smallest edits needed to remove the identified patterns.

Review the final diff sentence by sentence for semantic drift and unnecessary
rewriting. Search the edited scope for remaining em dashes, run applicable
formatting or content checks, and summarize the concrete patterns removed.
