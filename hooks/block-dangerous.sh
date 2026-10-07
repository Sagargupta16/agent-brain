#!/usr/bin/env bash
# PreToolUse hook: block obviously destructive bash commands.
# Exit 2 = block. Exit 0 = allow.

set -u
CMD=$(jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$CMD" ] && exit 0

# Disk-wide destructive commands
if echo "$CMD" | grep -qE '(^|[^a-zA-Z0-9_])rm[[:space:]]+(-[rRf]+[[:space:]]+)?/($|[[:space:]])'; then
  echo "blocked: rm on root directory" >&2
  exit 2
fi

if echo "$CMD" | grep -qE '(^|[^a-zA-Z0-9_])rm[[:space:]]+-rf?[[:space:]]+~'; then
  echo "blocked: rm -rf on home directory" >&2
  exit 2
fi

# Git destructives without explicit confirmation intent in the message
if echo "$CMD" | grep -qE 'git[[:space:]]+push[[:space:]]+(--force|-f)[[:space:]]+.*[[:space:]]+(main|master)($|[[:space:]])'; then
  echo "blocked: force-push to main/master. Push to a feature branch or get explicit permission." >&2
  exit 2
fi

if echo "$CMD" | grep -qE 'git[[:space:]]+(reset|checkout)[[:space:]]+--hard'; then
  # Don't hard-block but warn. These have legitimate uses.
  echo "warning: destructive git op. Verify intent before proceeding." >&2
fi

# No-verify bypass attempts
if echo "$CMD" | grep -qE 'git[[:space:]]+commit.*--no-verify'; then
  echo "blocked: --no-verify bypasses pre-commit hooks. Fix the hook issue instead." >&2
  exit 2
fi

# Em/en-dash ban in outbound text payloads (commits, PR bodies, comments, releases).
# Prompt-level rules slip; this blocks the dash characters mechanically.
if echo "$CMD" | grep -qE '^[[:space:]]*(git[[:space:]]+commit|gh[[:space:]]+(pr|issue|release|api))([[:space:]]|$)'; then
  # UTF-8 bytes: en-dash U+2013 = E2 80 93, em-dash U+2014 = E2 80 94
  if printf '%s' "$CMD" | LC_ALL=C grep -qE $'\xe2\x80\x93|\xe2\x80\x94'; then
    echo "blocked: em-dash or en-dash (U+2013/U+2014) in commit/PR/comment text. Replace with -- or - and retry." >&2
    exit 2
  fi
fi

exit 0
