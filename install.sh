#!/usr/bin/env bash
# Install agent-brain for one or more agent hosts.
#
#   ./install.sh                     # Claude Code only
#   ./install.sh --host codex        # one host
#   ./install.sh --host all --seed   # every host, and seed the brain with the public learnings
#   ./install.sh --dry-run ...       # print what would change, change nothing
#   ./install.sh --register-mcp      # also run `claude mcp add` / `codex mcp add` (off by default)
#
# Never overwrites a file it did not write: existing skills and rules are skipped
# unless --force. Digest blocks in AGENTS.md files sit between markers and are
# replaced in place on re-run.

set -u
REPO="$(cd "$(dirname "$0")" && pwd)"
HOSTS="claude"
SEED=0
FORCE=0
DRY=0
REGISTER=0
BRAIN_DIR="${AGENT_BRAIN_DIR:-$HOME/.agent-brain}"

while [ $# -gt 0 ]; do
  case "$1" in
    --host) HOSTS="$2"; shift 2 ;;
    --brain) BRAIN_DIR="$2"; shift 2 ;;
    --seed) SEED=1; shift ;;
    --force) FORCE=1; shift ;;
    --dry-run) DRY=1; shift ;;
    --register-mcp) REGISTER=1; shift ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
[ "$HOSTS" = "all" ] && HOSTS="claude codex kiro"

PY="$(command -v python3 || command -v python || true)"
[ -z "$PY" ] && { echo "python 3.10+ is required for the brain CLI" >&2; exit 1; }
BRAIN_CMD="$PY $REPO/bin/brain.py"

run() { if [ "$DRY" = 1 ]; then echo "would: $*"; else "$@"; fi; }

copy_dir() {  # copy_dir <src> <dest>: skip an existing dest unless --force
  if [ -e "$2" ] && [ "$FORCE" = 0 ]; then echo "skip (exists): $2"; return; fi
  run mkdir -p "$(dirname "$2")"
  [ -e "$2" ] && run rm -rf "$2"
  run cp -R "$1" "$2"
  echo "installed: $2"
}

put_digest() {  # put_digest <file>: insert or replace the marked digest block
  local file="$1" begin="<!-- agent-brain:begin -->" end="<!-- agent-brain:end -->"
  if [ "$DRY" = 1 ]; then echo "would: write digest block into $file"; return; fi
  mkdir -p "$(dirname "$file")"
  touch "$file"
  "$PY" - "$file" "$REPO/AGENTS.md" "$begin" "$end" <<'PY'
import pathlib, sys
target, digest, begin, end = sys.argv[1:]
text = pathlib.Path(target).read_text(encoding="utf-8")
block = f"{begin}\n{pathlib.Path(digest).read_text(encoding='utf-8').strip()}\n{end}\n"
if begin in text and end in text:
    head, rest = text.split(begin, 1)
    text = head + block + rest.split(end, 1)[1].lstrip("\n")
else:
    text = (text.rstrip("\n") + "\n\n" if text.strip() else "") + block
pathlib.Path(target).write_text(text, encoding="utf-8")
PY
  echo "digest: $file"
}

mcp_hint() { echo "register MCP yourself: $*"; }

# ---- the brain folder (shared by every host) ----
run mkdir -p "$BRAIN_DIR"
if [ "$SEED" = 1 ]; then
  for f in "$REPO"/brain/learnings/*.md; do
    [ "$(basename "$f")" = "README.md" ] && continue
    dest="$BRAIN_DIR/$(basename "$f")"
    if [ -e "$dest" ] && [ "$FORCE" = 0 ]; then continue; fi
    run cp "$f" "$dest"
  done
  [ "$DRY" = 0 ] && $BRAIN_CMD --dir "$BRAIN_DIR" index >/dev/null
  echo "seeded: $BRAIN_DIR"
fi

for host in $HOSTS; do
  echo "== $host"
  case "$host" in
    claude)
      for d in "$REPO"/skills/*/; do copy_dir "${d%/}" "$HOME/.claude/skills/$(basename "$d")"; done
      for d in "$REPO"/agents/*.md; do copy_dir "$d" "$HOME/.claude/agents/$(basename "$d")"; done
      for r in always-on python js infra; do copy_dir "$REPO/rules/$r.md" "$HOME/.claude/rules/$r.md"; done
      echo "hooks ship with the plugin: /plugin marketplace add Sagargupta16/agent-brain, then /plugin install agent-brain@agent-brain"
      if [ "$REGISTER" = 1 ] && command -v claude >/dev/null 2>&1; then
        run claude mcp add --scope user agent-brain -e "AGENT_BRAIN_DIR=$BRAIN_DIR" -- "$PY" "$REPO/bin/brain.py" mcp
      else
        mcp_hint "claude mcp add --scope user agent-brain -e AGENT_BRAIN_DIR=$BRAIN_DIR -- $PY $REPO/bin/brain.py mcp"
      fi
      ;;
    codex)
      CODEX="${CODEX_HOME:-$HOME/.codex}"
      for d in "$REPO"/skills/*/; do copy_dir "${d%/}" "$CODEX/skills/$(basename "$d")"; done
      put_digest "$CODEX/AGENTS.md"
      if [ "$REGISTER" = 1 ] && command -v codex >/dev/null 2>&1; then
        run codex mcp add agent-brain --env "AGENT_BRAIN_DIR=$BRAIN_DIR" -- "$PY" "$REPO/bin/brain.py" mcp
      else
        mcp_hint "codex mcp add agent-brain --env AGENT_BRAIN_DIR=$BRAIN_DIR -- $PY $REPO/bin/brain.py mcp"
      fi
      ;;
    kiro)
      for d in "$REPO"/skills/*/; do copy_dir "${d%/}" "$HOME/.kiro/skills/$(basename "$d")"; done
      put_digest "$HOME/.kiro/steering/agent-brain.md"
      mcp_hint "add to ~/.kiro/settings/mcp.json: \"agent-brain\": {\"command\": \"$PY\", \"args\": [\"$REPO/bin/brain.py\", \"mcp\"], \"env\": {\"AGENT_BRAIN_DIR\": \"$BRAIN_DIR\"}}"
      ;;
    *) echo "unknown host: $host (claude, codex, kiro, all)" >&2; exit 2 ;;
  esac
done

echo "== done. Try: $BRAIN_CMD --dir $BRAIN_DIR recall lockfile"
