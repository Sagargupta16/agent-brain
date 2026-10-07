---
name: subagent-denials-cannot-be-retried
description: "In auto mode, once the classifier denies a subagent an action, the main agent redoing the same outcome is blocked as Auto-Mode Bypass; do dependency and CLAUDE.md edits in the main session"
type: feedback
source: "observed 2026-09-30 to 2026-10-01 during a dependency cleanup run through parallel subagents"
created: 2026-10-01
modified: 2026-10-07
status: active
visibility: public
---

The auto-mode safety classifier judges each action in context. A subagent told by the coordinator (not by the user) to remove two backend dependencies from `pyproject.toml`, re-run `uv lock`, and edit `CLAUDE.md` was denied ("Modify Shared Resources"; agent requests cannot authorize CLAUDE.md edits). When the main agent then tried the same edits, the classifier blocked it as "Auto-Mode Bypass" and required reverting and asking the user. It only went through after the user asked for it directly.

**Why:** the block read as friction to the user because their permission rules already allowed the edits. The denial came from the classifier, not from `settings.json`.

**How to apply:**

- Do edits to dependency manifests and lockfiles, `CLAUDE.md`, and permission or config files in the main session, not via a subagent, so the user's own request is the authorization in context.
- If a subagent reports such a denial, do not retry the same outcome. Tell the user in one line what was blocked and that a direct "do it" (or a different permission mode) clears it.
- Explain that the block is the auto-mode classifier, not their permission rules, so they do not hunt for a permission they already granted.

Related: [[multi-agent-fanout-workflow]], [[agent-harness-gotchas]].
