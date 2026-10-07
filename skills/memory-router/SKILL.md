---
name: memory-router
description: >-
  Decide where one piece of session knowledge belongs and the exact format to
  write it in. Destinations are user-level rules files (how the user works,
  any repo), the brain at $AGENT_BRAIN_DIR (facts that outlive the session),
  project-scoped memory (one repo), STATUS.md or TODO.md (live or parked
  state), an owning doc (a deployments or tooling-decisions doc, repo
  CLAUDE.md, README, CHANGELOG), or discard. Called by save-session per item.
  Also use standalone when the user says "add this to memory", "add in user
  rule", "add in global memory", "add in project memory", "where should this
  go", or "save this" about a single fact.
---

# memory-router

Input: one item, `claim | evidence | date`, plus the current cwd. Output: a
destination, a file path, and the exact text shape to write. Never writes
anything itself when called by save-session; when used standalone it writes
the one item and prints the absolute path.

Two tests decide almost everything:

- **Test 1.** Does it prescribe behavior ("always", "never", "before X do Y")?
  Then a rules file or a `CLAUDE.md`.
- **Test 2.** Is it a fact about the world that could change? Then `STATUS.md`
  if it is live, the brain if it is cross-session.

Everything below is those two tests plus scope and volatility.

## Classify first

Answer these five for the item:

| Question | Values |
| --- | --- |
| scope | one repo / several repos / all repos / not about a repo |
| kind | rule / correction-incident / decision / gotcha / env-fact / repo-fact / live-state / measurement / personal / idea / activity / secret |
| volatility | stable / may change / dead within 30 days |
| asked | did the user explicitly say remember, save, memory, rule? |
| owner_doc | does a doc already own this topic? (a deployments doc owns hosting and dependency-bot cadence, a tooling-decisions doc owns tool choices, a git-workflow doc owns branching, a skill's `references/` owns its domain, a repo `CLAUDE.md` owns that repo's conventions) |

## Decision table

| Signal | Test | Destination | Shape |
| --- | --- | --- | --- |
| rule, scope=all, about how the user works with any agent ("never `&&`", "no em dash", "first make it exist", "one PR per work stream") | 1 | user-level rules file for behavior (for Claude Code, `~/.claude/rules/*.md`), a vocabulary rules file for what a phrase means | one imperative bullet under the matching `##`, trigger case and date in parentheses |
| rule, scope=all, a code-class pattern (a money-cell component, a chart date cap, a page wrapper) | 1 | brain `type: feedback` and the owning skill's `references/` | brain file; skill reference gets the snippet |
| rule, scope=one repo, needed every session there ("build output is `build/` not `dist/`") | 1 | the repo's `CLAUDE.md` if it has one; else project memory `type: project` | one bullet under the nearest `CLAUDE.md` section; keep the file under ~250 lines |
| correction-incident (the user corrected you and it changed behavior) | 1 | project memory `type: feedback`; if scope=all, the brain `type: feedback`; a second occurrence anywhere promotes it to a rules file | memory file with **Why:** (dated, user's words quoted) and **How to apply:** |
| decision, scope=all or several ("dependency bot: one grouped PR per repo per month", "no subdomains", "model choice") | 2 | `STATUS.md` when actionable, plus the owner_doc; planned or parked -> `TODO.md` | STATUS bullet under `## <topic> (<YYYY-MM-DD>) -- <STATE>`; TODO section with `**Status**: Planned/Parked (<date>)` and `Decided <date>: <choice> (<reason>)` |
| decision, scope=one repo ("article format locked", "dev data disposable", "tests not required for now") | 2 | project memory `type: project`, dated; a behavior change also goes to the repo `CHANGELOG.md` | memory file; CHANGELOG entry under the concrete next version, never `Unreleased` |
| gotcha or env-fact, scope=all (a cloud inference-profile quirk, PowerShell 5.1 has no `&&`, a stopped Windows service, `cmd /c npx` for MCP on Windows) | 2 | brain `type: reference`; if it gates a session or touches credentials by name, also the workspace `CLAUDE.local.md` | memory file with the exact error text and the fix that worked |
| gotcha or env-fact, scope=one repo (serverless DB driver, CSS framework scanning, a hosting adapter) | 2 | project memory `type: reference` | memory file, error text plus fix |
| repo-fact (architecture, data model, deploy split) | 2 | project memory `type: project`; contributor-facing detail -> README or docs, memory points there | memory file; README section |
| live-state (PR numbers and state, CI, deploy, counts, unfinished items, next command) | 2, dead within 30 days | `STATUS.md` in the workspace root; a project-local dated status file for pipelines; NEVER a memory file | dated bullet that includes the query or command that produced the number |
| measurement (a number with formula, script or command) | 2 | project memory `type: reference`, or the repo's own `references/` when the repo is the knowledge base; tag "re-measure before publishing" | memory file with formula, script path, date measured |
| personal, changes how to work with the user (work setup, accounts, devices, taste, taxonomy) | 2, scope=all | brain `type: user` | memory file indexed under `## User` |
| personal, a life decision in flight | 2 | brain `type: project` | memory file; never a repo doc |
| personal identifier (booking reference, order number, phone, address, salary, account number) | -- | discard the identifier; keep only the derived fact | receipt line only |
| idea, not started | 2 | `TODO.md` in the workspace root | `## <Idea>` section, `**Status**: Parked (<date>)` |
| activity ("merged #N", "fixed 47 Sonar issues") | -- | `STATUS.md` only if workspace state changed; otherwise discard | STATUS bullet |
| secret or cookie value | -- | discard the value; print `rotate <NAME>` | never written anywhere |
| anything about a fork of someone else's repo | policy | the brain or project memory only; never a file inside the fork | memory file |
| asked=true and nothing above matched | explicit ask wins | project memory `type: project` (the brain if scope=all); echo the absolute path | memory file |

## Tie-breaks, in order

1. Applies in more than one repo -> go up one level. The brain `INDEX.md` is
   read at every session start; a project memory is invisible from any other
   repo. A decision or a sibling-repo fact saved only in one repo's memory is
   the classic way knowledge gets lost.
2. Prescriptive beats descriptive. A rule goes to a rules file; the incident
   that produced it goes to memory. Never store only the story.
3. False within 30 days -> `STATUS.md`, `TODO.md` or a status file. Never
   memory. Counts are the classic case.
4. An owner_doc exists -> update the owner; at most a one-line pointer in
   memory. Two sources for one fact will drift.
5. Same fact never twice. A dedupe hit (`brain recall`) means update in place
   and report "updated".
6. An explicit remember/save/memory ask always writes at least one file and
   echoes the path, even when the table says discard.
7. Secrets and identifiers are stripped before any of the above.
8. Still undecided between the brain and project memory -> the brain plus a
   wikilink line in the project memory index.

## Paths

- Brain: `$AGENT_BRAIN_DIR` (default `~/.agent-brain`), index `INDEX.md`.
  Write with `brain remember`, read with `brain recall`, check with
  `brain lint`. Create `INDEX.md` with the four headings if missing.
- Project memory: your agent's per-project memory dir if it keeps one;
  otherwise a brain file whose `description` names the repo.
- Rules: your agent's user-level rules files (for Claude Code,
  `~/.claude/rules/*.md`).
- Live state: optional `STATUS.md` and `TODO.md` in the workspace root.
- Session-gating local notes: the workspace `CLAUDE.local.md` (never
  committed).

## Exact formats

Memory file (the canonical shape; write canonical, never rewrite legacy files
that use a different frontmatter):

```
---
name: <kebab-case-lesson-name>
description: "<one line stating the lesson itself, not the topic>"
metadata:
  node_type: memory
  type: user | feedback | project | reference
  modified: <ISO 8601 UTC>
---

<one paragraph stating the fact or rule, absolute dates>

**Why:** <incident or measurement, the user's words quoted, date>

**How to apply:** <imperative bullets; include when it does NOT apply>

Related: [[other-memory-name]]
```

Name the file by the lesson (`cpp-solutions-use-vector-never-arrays.md`),
never by session or date. Add `originSessionId` under `metadata` when the
session id is known.

`INDEX.md` line, under `## User` / `## Feedback` / `## Project` /
`## Reference`:

```
- [{{Title}}]({{file-name}}.md) - <one-line summary with the key number or rule>
```

Rules file: an imperative bullet under the existing matching section, trigger
case and date in parentheses.

Vocabulary rules file: `- **\`<phrase>\`** = <meaning>. <what to do>.` under
the matching `##`.

`STATUS.md`: keep the `> Last updated: <YYYY-MM-DD> (<what changed>)` line
current; sections `## <topic> (<YYYY-MM-DD>) -- <STATE>`; PR links as
`[owner/repo#N](https://github.com/owner/repo/pull/N)`; every count carries its
source query.

`TODO.md`: `## <Idea>`, `**Status**: Planned | Parked (<date>)`, bullets,
`Decided <YYYY-MM-DD>: ...`.

Repo `CLAUDE.md`: any shared preamble stays verbatim; one bullet under the
nearest section; file stays under ~250 lines.

`CHANGELOG.md`: Keep a Changelog headings under a concrete next version.

## Never

- Never write a secret value, cookie, booking reference, order number, phone
  number or address anywhere. Names only.
- Never create a memory file for live state or a count.
- Never write inside a fork of someone else's repo.
- Never write to `.claude/handoffs/`; nothing reads it.
- Never an em or en dash character; `--` or `-`.
- Never a relative date.
