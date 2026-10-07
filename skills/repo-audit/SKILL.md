---
name: repo-audit
description: >-
  Whole-repo deep analysis of one repo that ends in a findings report and
  waits for the user's "fix". Runs the repo's own gates once for a baseline,
  then sweeps correctness bugs, security, performance, dead code, dependency
  currency, CI and docs drift, and mobile-friendliness, each with file and
  line evidence, ranked by severity. Use when the user says "analyze this
  repo in very detail, find bugs", "analyse this repo in detail", "analyze
  again complete repo", "give me report", or "study this repo" about a whole
  codebase rather than a diff. Never edits code, never claims a bug without
  the line and command that shows it, and never starts fixing before the
  user says fix.
---

# repo-audit

A common ask is a whole-repo read that ends in a report: "analyze this repo in
very detail, find bugs", "analyze again complete repo", then "give me report".
`code-review` sees a diff, a graph tool explains structure; nothing owns the
deep single-repo pass. Read-only by design: the fix is the user's next
message.

## Read first

- Your always-on rules, if you keep them (honesty and verification; a
  described problem gets an assessment, not a patch)
- The repo's `CLAUDE.md`, `README.md`, `TODO.md`, `docs/` index, the last 30
  commits (`git log --oneline -30`), open issues (`gh issue list --state open`)
- `graphify-out/` when present and the graphify skill is installed:
  `graphify query "<question>"` before grepping for architecture questions

## Procedure

1. Header first: repo, branch, `git rev-parse --short HEAD`, files by language
   (`git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head`), entry
   points, deploy target. Print it before anything else.
2. Baseline the repo's own gates once, exactly as its `CLAUDE.md` names them
   (`pnpm run check`, `uv run pytest`, `npm run typecheck`, `pnpm build`).
   Record pass/fail with counts. A red baseline is finding #1, not a stop.
3. Sweep in lanes. Over ~150 source files, fan the lanes out with the `parallel`
   skill (one read-only agent per lane, shared return shape
   `file:line | severity | claim | evidence | one-line fix`); below that, run
   them yourself in this order.

| Lane | Look for | Evidence required |
| --- | --- | --- |
| correctness | off-by-one, null paths, unawaited promises, wrong SQL dialect calls (a SQLite-only function on a Postgres backend), timezone anchors that disagree with the repo's rule, swallowed exceptions | the line plus a repro command or failing input |
| security | secrets in history (`git log -p -S ghp_`, `-S AKIA`, `-S sk-`), tracked `.env`, string-built SQL or URLs, CORS `*`, unauthenticated route, missing `user_id` scoping | line and the command that showed it |
| performance | N+1 queries, sync I/O in request paths, unbounded lists or recursion, long lists without virtualisation, eager pages | line plus the loop or query count |
| structure | dead exports, duplicated helpers, files over the repo's own size rule, barrels where its `CLAUDE.md` forbids them | grep counts, not opinion |
| deps | `pnpm outdated`, `pnpm audit`, `uv pip list --outdated`, `gh api repos/<owner>/<repo>/dependabot/alerts?state=open --jq length`; treat outdated as a defect | the command output |
| ci and docs | `gh run list --limit 10` per workflow; README or CHANGELOG claims the code no longer matches | run ids; details go to `gh-actions` and `docs-fresh` |
| mobile | anything web-facing: layout at 375px, tap targets under 44px, tables that scroll sideways, `h-screen` where `h-dvh` is the rule | component and the viewport width it fails at |

4. Deduplicate across lanes, then rank: critical (data loss, auth, secrets),
   high (wrong output, red gate, vulnerable dep), medium (perf, structure),
   low (style, docs). A finding without evidence is dropped, not softened.
5. Verify the top ten yourself before publishing: open the file, run the repro.
   Subagent findings are claims until you looked: the summary describes
   intent, not reality.
6. Print the report and stop. The last line is the offer. When the user
   answers "fix", "fix all", or names numbers ("do 1, 3, 4"), the report is
   the worklist for `fix-all` (enumerate-first, `fixed N/N`); a single named
   finding is fixed inline on a branch and verified the way its evidence
   column says.

## Output

```
repo <owner>/<repo> @ <sha> on <branch> | 412 files (ts 288, py 61, md 24) | <YYYY-MM-DD>
baseline: pnpm run check FAIL (2 type errors) | tests 212/214 | build pass

| # | sev | lane | file:line | finding | evidence | fix (one line) |
| 1 | critical | security | backend/api/upload.py:88 | soft delete not user-scoped | grep shows no user_id predicate on the query | add user_id filter |
| ... |

counts: critical 1, high 4, medium 9, low 6 (20 total, 20 with evidence)
skipped on purpose: <area> (reason)
say "fix" to run fix-all on this list, or name the numbers to do.
```

## Must not

- Never edit, format, commit, or open a PR from this skill; report only.
- Never state a bug without `file:line` plus the command or input that shows
  it; "looks suspicious" is not a finding.
- Never stop at the first hits in a lane; grep the full set and give counts.
- Never pad with generic advice (add tests, add docs, enable strict); each
  finding names this repo's line.
- Never audit an upstream fork as if it were the user's own; its bugs go
  through the `oss` skill and its 7/10 bar.
- Never read `.env*` or local database file contents; tracking state and
  existence are the findings, never the values.
- Never chain commands with a double ampersand; one per line.

## Non-goals

Diff review (`code-review`), architecture explanation (graph or diagram
skills, if installed), the fix itself (`fix-all`), docs rewrite
(`docs-fresh`), CI repair (`gh-actions`), design critique (a design skill, if
installed).
