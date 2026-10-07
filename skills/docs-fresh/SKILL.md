---
name: docs-fresh
description: >-
  Docs freshness pass for one repo. Lists every doc surface (README,
  CHANGELOG, docs/, CLAUDE.md, .env.example), checks each documented claim
  (commands, paths, env var names, counts) against current code, prints the
  drift table, then fixes in place in the repo's own voice and CHANGELOG
  convention. Use when the user says "update all docs md files as well",
  "all docs up to date? changelog, readme and docs folder", "also remember
  to update docs, changelog, readme if required", or "also update readme,
  claude md and changelog". Never edits generated docs output,
  release-please changelogs, or marker-fenced README blocks, or documents a
  feature the code lacks.
---

# docs-fresh

Usually appended to a feature turn ("update all docs md files as well"), or
the audit form ("all docs up to date? changelog, readme and docs folder").
Diagram tools draw and graph tools explain; nothing checks prose against code.
This does: claims in, evidence out, then edits.

## Read first

- Your always-on rules, if you keep them (editing files: Edit tool, CRLF;
  output style)
- Any writing-voice notes in the brain (`brain recall voice`): honest over
  marketing, specific over general, chat typos never propagate into a doc
- The repo's `CLAUDE.md`: it names generated dirs (for example a `docs/`
  folder that is the Pages build output, never hand-edited) and the changelog
  owner (for example release-please)
- The head of the repo's own `CHANGELOG.md` before writing one line into it

## Procedure

1. Enumerate the surfaces and print the count:
   `git ls-files '*.md' 'docs/**' '.env.example' 'CHANGELOG*'`
   plus any file the `CLAUDE.md` calls documentation, minus what it marks
   generated.
2. Find the drift window per file: `git log -1 --format=%cI -- README.md` is
   the doc's last touch; `git diff --stat <that-commit>..HEAD -- . ':!*.md'` is
   the code that moved since. Older than its code makes a doc a candidate, not
   yet a finding.
3. Extract every checkable claim from each doc and test it against the tree:

| Claim type | Check |
| --- | --- |
| command or script (`pnpm run check`, `uv run pytest`) | exists in `package.json` scripts, `pyproject.toml`, `Makefile`; run the harmless ones (`--help`, `--version`) |
| path or file mentioned | `ls` it; renamed dirs are the most common drift |
| env var | every prefixed name the code reads (`grep -rhoE 'APP_[A-Z_]+' backend/ \| sort -u`, with the repo's own prefix) appears in `.env.example` and the docs table; names only, never values |
| count ("26 protected pages", "15 read-only tools") | count in code (`grep -c`, `ls pages`) and compare |
| version or dependency claim | `package.json`, `pyproject.toml`, the lockfile |
| badge, link, anchor | target file or heading exists; external URL answers 200 to `curl -sI` |
| screenshot or diagram | the UI or module it shows still exists; a stale image is a finding, the redraw is a diagram task |

4. Print the drift table before editing (shape below). Zero drift is a valid
   result: say so with the counts and stop.
5. Edit each finding in place with the Edit tool, matching the file's heading
   levels, table style, and register. Numbers come from step 3, never from
   memory.
6. CHANGELOG, only when the repo keeps one and the convention is read from its
   head: Keep-a-Changelog repos (`## Unreleased`, then `Added`, `Changed`,
   `Fixed`, `Security`) get the entry under `Unreleased`; versioned repos
   (`## [2.3.4] - <YYYY-MM-DD>`, matching `version` in the manifest) get the
   entry under the heading for the manifest version, and a new heading only if
   this work bumped it; release-please repos get nothing by hand.
7. Verify by re-running step 3 on every edited file: each claim resolves, each
   link and path exists, `git diff --stat` lists only the files in the table.
8. Leave the edits uncommitted unless the same message asked to push; then
   `ship`.

## Output

```
surfaces: 14 files (README, CHANGELOG, docs/ x9, CLAUDE.md, AGENTS.md, .env.example)
drift window: README last touched <YYYY-MM-DD>, 61 code files changed since

| file | claim | in doc | in code | action |
| README.md | backend port | 5000 | 8000 (`vite.config.ts` proxy) | fixed |
| docs/PAGES.md | protected routes | 24 | 26 (`App.tsx`) | fixed |
| .env.example | APP_DAILY_MESSAGE_LIMIT | missing | read in settings.py:88 | added (name only) |
| docs/architecture.md | OAuth diagram | v1 flow | PKCE v2 | flagged for redraw |

fixed 11/12 | flagged 1 | changelog: Unreleased/Changed +1 line | commit: not asked
```

## Must not

- Never edit generated output: a built `docs/` site, anything between
  `<!-- ...:START -->` and `<!-- ...:END -->` markers in a README,
  `metrics/`, or a release-please changelog.
- Never invent a version heading, a date, or a feature; if the code does not
  do it, the doc does not say it.
- Never turn a README into marketing copy or add badges, emoji, or dash
  characters; match the file that is there.
- Never `sed -i` or rewrite a whole file; CRLF repos turn that into a
  full-file diff.
- Never remove existing content (footers, credits, licence lines, contributor
  tables) while refreshing.
- Never commit; the ask was to update, and `ship` commits when asked.
- Never chain commands with a double ampersand; one per line.

## Non-goals

Diagrams (a diagram skill, if installed), code changes the docs reveal as
missing (`repo-audit` finding, then `fix-all`), memory files and STATUS.md
(`save-session`, `memory-router`).
