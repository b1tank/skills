---
description: "Use when verifying website or UI changes in a browser — opening pages, taking screenshots, reading page content, clicking, typing, navigating, or otherwise smoke-checking front-end work. Defines which browser toolset to reach for first."
---
# Browser verification

When you need to actually open a page to verify a change, the order is:

0. **Cheapest — `fetch_webpage` (no rendering).** If the check is purely
   about *what bytes come back* — "does this URL 200?", "is the new
   `<meta>` tag present?", "is the footer text updated?" — use
   `fetch_webpage` first. No browser, no JS execution, no screenshot churn.
   Skip this tier the moment you need to see rendered DOM, computed CSS,
   client-side routing, or anything JavaScript produces.

1. **Default — VS Code integrated browser tools.** Use these for every routine
   verification that needs a real browser:
   - `open_browser_page` to open a URL (and to reuse pages — prefer the
     `pageId` of an already-open tab over opening a new one)
   - `navigate_page` to navigate, reload, or go back/forward
   - `read_page` for an accessibility snapshot when you need structure
   - `screenshot_page` for a visual snapshot
   - `click_element`, `type_in_page`, `hover_element`, `drag_element`,
     `handle_dialog` for interactions
   - `run_playwright_code` for one-off scripted actions (scroll, evaluate
     expressions) — go through the `page` object, never touch `document` or
     `window` directly

2. **Fallback — Playwright MCP (`mcp_playwright_browser_*`).** Only reach for
   these when the integrated browser can't do the job. Typical reasons:
   - need multi-tab orchestration (`mcp_playwright_browser_tabs`)
   - need network-level inspection (`mcp_playwright_browser_network_requests`)
   - need browser console messages (`mcp_playwright_browser_console_messages`)
   - need a capability the integrated tools genuinely lack (file uploads,
     keyboard chords, resize the browser viewport, etc.)
   - the integrated tools fail in a way that isn't user error (e.g. wrong tab
     is captured and can't be selected by `pageId`)

   If you fall back, say briefly why in the message that uses the MCP tool.

3. **Never** use `xdg-open`, `open`, `start`, `gio open`, or any shell command
   that hands the URL off to the host OS. Both browser toolsets above are
   strictly preferred.

## Discipline
- Reuse pages: pass the existing `pageId` instead of calling
  `open_browser_page` again for the same host.
- One screenshot per checkpoint is usually enough — don't spam the chat with
  full-page captures when an accessibility snapshot answers the question.
- After verification, stop. Don't leave dev servers, browser tabs, or
  Playwright sessions running unless the user asked for an ongoing session.
