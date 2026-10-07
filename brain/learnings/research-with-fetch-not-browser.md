---
name: research-with-fetch-not-browser
description: "Do web research with fetch and search tools, never browser automation; keep Playwright and DevTools for UI testing and debugging"
type: feedback
source: "working-style rule set 2026-07-06 after slow browser-driven research sessions"
created: 2026-07-06
modified: 2026-10-07
status: active
visibility: public
---

For research tasks (fact-checking, pricing or docs lookup, "dig on the internet"), use a web-fetch tool and a search API only. Do not use Chrome DevTools MCP or Playwright browser automation for research.

**Why:** browser automation for simple page reads is slow and heavy, and it burns context on page snapshots. Playwright and DevTools remain the right tools for their real purpose: UI verification, debugging, and testing local apps.

**How to apply:** when writing workflow scripts or subagent prompts that involve web research, include an explicit line such as "Do NOT use Playwright or Chrome DevTools browser tools; use web fetch and search only."

Related: [[agent-execution-patterns]].
