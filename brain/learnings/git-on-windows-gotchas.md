---
name: git-on-windows-gotchas
description: "Git and GitHub traps on Windows checkouts -- CRLF noise, rebase blocked by unwritable files, gofmt on CRLF, fork detachment after a visibility flip"
type: reference
source: "observed across several repos and an upstream Go provider fork on Windows, last seen 2026-10-01"
created: 2026-10-01
modified: 2026-10-07
status: active
visibility: public
---

- **CRLF noise inflates dirty counts.** With `core.autocrlf=true` and no `.gitattributes`, line-ending flips show up as modified files. Do not commit the flip: if the diff is pure CRLF, `git checkout -- <file>`. Tools like `sed -i` silently rewrite a CRLF file to LF and produce a whole-file diff; use an editor or a `newline=''` Python rewrite and byte-check `\r\n` vs bare `\n` afterwards.
- **"cannot rebase: You have unstaged changes" when nothing is really dirty.** In a large upstream repo, git failed to write a handful of files under a deep `testdata/` directory, and those phantom changes blocked checkout and rebase. Fix: `git checkout -- .` then `git rebase --continue`.
- **`gofmt -l` flags every file in a CRLF checkout.** Check formatting on an LF copy instead: `tr -d '\r' < f.go | gofmt -d`.
- **Fork detachment.** Making a forked repo private and then public again breaks its fork relationship, so it can no longer open PRs upstream. Fix: clone the branch, delete the repo, re-fork, push the branch, open a new PR.
- **`gh auth refresh` with scopes times out in a background shell.** Use the manual browser auth flow in a foreground terminal.

Related: [[windows-bash-gotchas]].
