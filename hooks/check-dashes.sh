#!/usr/bin/env bash
# PreToolUse hook on Write|Edit: block NEWLY INTRODUCED em/en-dashes (U+2014/U+2013).
# The style rule bans them everywhere; only new text is checked, so editing
# upstream files that already contain them still works.
# Exit 2 = block. Exit 0 = allow.

set -u
INPUT=$(cat)

NEW=$(printf '%s' "$INPUT" | jq -r '.tool_input.new_string // .tool_input.content // .tool_input.new_source // empty' 2>/dev/null)
[ -z "$NEW" ] && exit 0

# UTF-8 bytes: en-dash U+2013 = E2 80 93, em-dash U+2014 = E2 80 94
DASH=$'\xe2\x80\x93|\xe2\x80\x94'
if ! printf '%s' "$NEW" | LC_ALL=C grep -qE "$DASH"; then
  exit 0
fi

# Edit: allow if the dash was already present in the replaced text (preserving upstream style).
OLD=$(printf '%s' "$INPUT" | jq -r '.tool_input.old_string // empty' 2>/dev/null)
if [ -n "$OLD" ] && printf '%s' "$OLD" | LC_ALL=C grep -qE "$DASH"; then
  exit 0
fi

echo "blocked: new text introduces em-dash or en-dash (U+2013/U+2014). Replace with -- or - and retry." >&2
exit 2
