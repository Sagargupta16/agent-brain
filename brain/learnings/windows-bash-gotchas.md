---
name: windows-bash-gotchas
description: "Git Bash / MSYS traps on Windows -- CRLF in tool stdout, jq negation, base64 from the GitHub API, PowerShell vs MINGW paths, stale npm global prefix"
type: reference
source: "collected 2026-05-13 to 2026-09-19 from agent sessions running Git Bash on Windows 11"
created: 2026-05-13
modified: 2026-10-07
status: active
visibility: public
---

Each item is a failure and the fix that worked.

- **CRLF in `python3` / `node` stdout.** When bash parses their output on Git Bash/MSYS, every line except the last carries a trailing `\r`. Downstream comparisons (`[[ -d "$path" ]]`, `[[ "$x" == "y" ]]`) then silently fail. Symptom seen 2026-05-13: a validator reported every plugin as "not found" except the last one in the list. Fix: pipe through `tr -d '\r'`.
- **jq `!=` gets mangled** by the shell layer. Use `select(.x == "y" | not)` instead.
- **base64 from the GitHub contents API** has embedded newlines. `tr -d '\n'` before `base64 -d`.
- **Background commands that need an interactive terminal do not work** (for example `gh auth refresh -s <scope>` times out). Run them in a foreground terminal or use the browser flow.
- **Commands handed to the user may run in PowerShell, not bash.** A MINGW path like `cd /c/src/project` fails there with `Cannot find path 'C:\c\src\project'`, and PowerShell 5.1 has no `&&` at all. To hand over a bash script, wrap it: `& 'C:\Program Files\Git\bin\bash.exe' -c "cd /c/src/project; bash <script>"`. See [[no-ampersand-chaining]].
- **Stale npm global prefix hides a leftover global install** (2026-09-19). After switching to nvm-windows, `npm -g uninstall <pkg>` was a silent no-op ("up to date") because npm's prefix had moved, while the old package and its shims still sat under the pre-nvm prefix `~/AppData/Roaming/npm`. Fix: `npm uninstall -g --prefix "$HOME/AppData/Roaming/npm" <pkg>`, then confirm with `which -a <bin>`. Do not wipe that directory; it also holds other global tools.

**How to apply:** check this list before debugging a "works on Linux, fails on Windows" shell script.

Related: [[no-ampersand-chaining]], [[git-on-windows-gotchas]], [[agent-harness-gotchas]].
