---
name: save-session
description: >-
  Save this session's learnings before /compact or /clear, in one fast turn.
  Use when the user says "save all learning", "save this in memory",
  "remember this" (also common typos like remeber or rember), "keep in mind",
  "add in global/user memory", "add in rule", "as of now" / "from now on" /
  "for now" with a standing instruction, "compact it", "before compact", or
  when a PreCompact hook reminder appears. Extracts corrections, decisions,
  gotchas, environment facts, live state, measurements and ideas; drops noise
  and secrets; dedupes against the existing brain; routes each survivor
  through memory-router to rules, the brain, STATUS.md, TODO.md or an owning
  doc; prints a short table ending "safe to /compact". Never writes a
  narrative handoff document.
---

# save-session

One fast, non-blocking turn. The user usually continues within minutes of
asking, so this skill extracts, dedupes, routes, writes and prints a receipt.
It does not summarise the session, does not ask questions, does not review or
test, does not commit.

Why it exists: the unit of continuity is usually one long-lived session that
gets compacted again and again, not a chain of fresh sessions. Handoff-style
tools write a narrative for the *next* session to a place nothing reads. The
loss happens *inside* the current session, right after compaction, and the fix
is memory that survives it plus a pointer the next turn actually reads.
Lessons behind the design:

- Save rules, decisions and gotchas, not "what was done". Activity is already
  in git log and STATUS.md.
- Every lesson saved only as a reaction to a complaint ("you forgot my
  pattern") was a lesson that should have been saved at the first compaction.
- Mid-task steers ("keep in mind", "as of now", "for now", "from now on") are
  extraction triggers with a scope attached, even when the user never says
  "memory".
- Counts quoted after compaction go stale; counts belong in a live-state file
  with a timestamp and the query that produced them, never in memory.
- The only cross-surface handoff that reliably works is plain chat text the
  user can paste; other agent surfaces may not read the same memory dir.

## Procedure

### 1. Scope

- Everything in context since session start, or since the last marker line
  `save-session: saved N items at <ISO time>` if one exists.
- Include any compaction summary already in context; its "Primary Request",
  constraints and pending-tasks sections are candidate sources.
- Record: cwd, repo, branch, and the brain dir `$AGENT_BRAIN_DIR` (default
  `~/.agent-brain`). If that dir has no `INDEX.md`, create it with the four
  headings `## User`, `## Feedback`, `## Project`, `## Reference`.

### 2. Extract candidates

Walk the scope and collect items into these buckets. Each item is one line:
`claim | evidence (turn or tool result) | date`.

| Bucket | Look for |
| --- | --- |
| correction | user turns with "you forgot", "why did you", "i said", "i told", "not asked", "wrong", "again" that changed what you did next |
| directive | "always", "never", "from now on", "as of now", "for now", "keep in mind", "my way", "my pattern", "in my style" |
| decision | a choice between options plus its reason: "go with", "hold", "drop this", "park it", "keep", "kill", "1 PR", numbered answers ("1 keep 2 kill") |
| gotcha | a failing command or API error paired with the fix that worked. Both halves required, or it is not a gotcha |
| env-fact | from tool output: ports, paths, IDs, versions, model IDs, which surface, "X was removed", token scopes by NAME only |
| live-state | PR numbers and state, CI results, deploy state, counts WITH the query that produced them, unfinished items, the exact next command |
| measurement | a number with its formula, script path or command, and the date measured |
| idea | "keep it in todo", "park", "someday", "what about", feature thoughts not started |

Mark each item **verified** (a tool result in this session shows it) or
**(unverified)**. Unverified items are still saved, tagged as such.

### 3. Drop noise

Discard anything that is:

- already in your user-level rules files, a `CLAUDE.md` (user, workspace or
  repo), or any `INDEX.md` line (`brain recall <key noun>` first)
- a transient error with no reusable cause
- activity narration that git log or `STATUS.md` already records
- a one-off UI nit
- agent-authored text: subagent prompts, worker chatter, your own plans
- a pasted third-party document, log, or web page

### 4. Secrets gate

Before routing, scan every item for `ghp_`, `github_pat_`, `sk-`, `AKIA`,
`eyJ`, `Bearer`, session cookie names (`sessionid`, `csrftoken`,
`cf_clearance`, `__stripe_mid`), `.env` values, and booking-reference /
order-number / phone-number / address / salary shaped strings.

- Strip the value. Keep the NAME. Never write a value anywhere, including the
  receipt.
- Add a `rotate:` line to the receipt naming each credential seen.
- Identifiers (booking reference, order number, phone) are dropped; keep only
  the derived fact ("share rises 2,000/month"), never the identifier.

### 5. Dedupe

For each surviving item, search before writing:

- `brain recall <key noun>` against `$AGENT_BRAIN_DIR`
- `INDEX.md` description lines
- headings and bullets in your user-level rules files
- file names in the brain, in kebab-case AND snake_case (older files may be
  snake_case)

A match means **update in place**: add a dated line under `**Why:**` or
`**How to apply:**`, bump `modified` in the frontmatter, report "updated".
Never create a second file for the same fact.

### 6. Route

Send each item through the `memory-router` skill. It returns a destination
and the exact format. Follow it; do not improvise a location.

### 7. Write

- `brain remember` for brain entries (or write the file directly and add its
  `INDEX.md` line; `brain index` rebuilds the index). Run `brain lint` after.
- Preserve each file's existing line endings; never `sed -i` a CRLF file.
- Absolute dates (`2026-09-22`), never relative.
- `--` or `-`, never an em or en dash character.
- One memory file per lesson, named by the lesson
  (`cpp-solutions-use-vector-never-arrays.md`), never by the session or date.
- Add the `INDEX.md` line under the right heading.
- `STATUS.md` (optional, workspace root): update the `> Last updated:` line.
- Repo doc edits stay uncommitted unless the same message asked to push.
  "also update the readme and changelog" is an edit ask, not a commit ask.
- Nothing is ever written inside a fork of someone else's repo.

### 8. Receipt

Print under ~25 lines, no prose:

```
| item | destination | file | new/updated |
| ... | ... | ... | ... |

not saved: <item> (duplicate) / <item> (transient) / <item> (agent-text)
unfinished: <open item> -> <exact next command>
rotate: <CREDENTIAL_NAME>, <CREDENTIAL_NAME>
next session reads: <$AGENT_BRAIN_DIR/INDEX.md>, <STATUS.md or status file path>

save-session: saved N items at <ISO time>
safe to /compact
```

The `next session reads:` line is plain text on purpose: other agent surfaces
may not read the brain dir, so this line is what the user pastes across
surfaces. The marker line scopes the next run and rides into the compaction
summary.

If nothing qualifies, print exactly: `nothing new to save; live state already
in STATUS.md` and the marker line.

## Non-goals

No narrative summary (users ask the agent to act, not to recap). No review
pass, tests, or commits. No `.claude/handoffs/`. No blocking questions. No
rewriting of legacy snake_case memory files. No touching generated content or
anything between `<!-- ...:START -->` markers.

## Standalone triggers

A single "remember this" or "add in user rule" mid-session runs steps 4 to 8
on that one item only and prints a one-line receipt with the absolute path.
An explicit ask always writes at least one file, even when the router would
otherwise discard.
