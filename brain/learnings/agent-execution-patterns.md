---
name: agent-execution-patterns
description: "Working-style rules for a coding agent -- execute when asked to do, ask once on ambiguous names, stop after two failed attempts, one PR per stream, never remove or change what was not asked"
type: feedback
source: "derived 2026-04 to 2026-06-10 from session-friction reports (wrong-approach and misunderstood-request events)"
created: 2026-06-10
modified: 2026-10-07
status: active
visibility: public
---

## Execute over plan by default

When the user asks to DO something (apply, rename, merge, deploy, fix), act immediately and report results after. Plan only when asked ("plan X", "how should we do X"). If a plan helps clarity, keep it to 3 lines and proceed unless the risk is high.

**Why:** friction reports showed sessions stalling because the agent defaulted to analysis when the user wanted action.

## Ask once on ambiguous names

When a short term could name several things (a product name, "the repo", a project nickname), ask "Which X do you mean, A or B?" before any write or destructive operation. If context makes it about 90% clear, state the assumption and proceed ("Assuming A, correct me if wrong"). Never assume silently on archive, delete or rename.

**Why:** single misreads cost whole sessions, including the wrong repo being archived. These are one-question-away fixes.

## Two failed attempts means stop and expose the logic

When a calculation or output is wrong twice, stop iterating. List every formula and assumption as bullets and ask which is wrong. When the user says revert, revert EVERYTHING from the attempt, verify the clean state, then confirm.

**Why:** iterating blind on wrong logic, and then a partial revert, burned trust faster than the original bug.

## Merge pipeline

- **One PR per work stream** until it merges. Push follow-up commits to the same branch instead of opening a second PR.
- **Green checks are the merge gate**, and the agent checks them. Check CI, merge, then confirm the deployment actually succeeded.
- **Docs, changelog and version numbers in sync** is part of "done".
- Projects with a `dev` branch go feature -> `dev`, then `dev` -> `main`. Never feature -> `main` directly.

## Do not remove or change what was not asked

- Never remove existing UI or content (footers, copyright lines, credits) during a refactor.
- Never change config values silently; explain the change and ask first.
- Before creating new assets (skills, configs), search for existing ones.
- Do not expand an integration's scope beyond the named ask.

Related: [[verify-integration-auth-first]], [[multi-agent-fanout-workflow]].
