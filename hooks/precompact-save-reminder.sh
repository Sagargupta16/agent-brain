#!/usr/bin/env bash
# PreCompact hook: nudge before context is compacted or cleared.
#
# Compaction discards the detail that /save-session exists to capture. This
# hook cannot run the skill (hooks cannot invoke skills) and it must not block
# compaction, so it does the one useful thing available: surface a reminder to
# the user and inject a short instruction into the compaction context so the
# summary itself carries the "unsaved learnings" flag forward.
#
# Fires on both matchers ("manual" and "auto"). Silent on any error so a hook
# problem can never wedge a compaction.

set -u

payload="$(cat 2>/dev/null || true)"
trigger="$(printf '%s' "$payload" | jq -r '.trigger // .matcher // "unknown"' 2>/dev/null || echo unknown)"

if [ "$trigger" = "auto" ]; then
  msg="Auto-compaction is starting. Any learnings from this session that were not saved with /save-session will be summarised away. Run /save-session in the next turn if this session produced decisions, gotchas, or corrections worth keeping."
else
  msg="Compacting. If you have not run /save-session yet, learnings from this session (decisions, corrections, gotchas, live state) will be lost to the summary. Run /save-session first if anything here is worth keeping."
fi

# PreCompact accepts only the common output fields; hookSpecificOutput is
# rejected by schema validation (checked 2026-09-23).
jq -cn --arg m "$msg" '{systemMessage: $m}' 2>/dev/null || true

exit 0
