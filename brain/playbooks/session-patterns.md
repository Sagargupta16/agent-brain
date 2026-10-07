---
name: session-patterns
description: "Agent session-start checklist, when to use subagents, user context-management signals, and how to run long multi-phase tasks"
type: playbook
source: "ported from a private multi-repo workspace playbook"
created: 2026-10-07
modified: 2026-10-07
status: active
visibility: public
---

# Session Patterns

## Session-start checklist

1. Read the workspace status file first (open PRs, CI health, action items) to understand the current state.
2. If it is more than 3 days old, offer to refresh it from live data.
3. When the user shares a PR link, always:
   - Check for new review comments.
   - Check CI status.
   - Check how far behind the base branch it is.
   - Suggest the next action (rebase, fix, reply, wait).
4. After PR-related work, update the status file.
5. Before deleting forks, verify zero open PRs.
6. When auditing repos, check `.gitignore`, `.env.example`, README, LICENSE.

## Subagents

Use them for research, bulk file scanning and parallel tracks; prompts must be self-contained because subagents do not see the parent context. Skip them for a single known read or grep, or anything that needs conversation history.

At the end of a multi-file change, spawn a fresh-context subagent to verify the diff against the task statement. Fresh eyes catch what self-review misses. Never commit on a workflow or subagent summary alone. See the learnings `multi-agent-fanout-workflow` and `subagent-denials-cannot-be-retried`.

## Signals that the user is managing context

- `/compact`, `/model`, `/clear` -- they are driving; do not narrate or assume continuity.
- `[Request interrupted by user]` -- they stopped the tool chain; do not restart the same approach.
- "Continue" -- pick up where you left off; they trust the direction.

## Long tasks

- Break into phases. Each phase is short, verifiable and committable.
- Save memory at phase boundaries; update the status file for multi-session work.
- Persist through the memory system (an index file plus one file per fact). Write memory early and often -- cheap to save, expensive to rediscover.
