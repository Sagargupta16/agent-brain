---
name: fix-all
description: >-
  The enumerate-first sweep. List every open finding for a repo or PR
  (failing CI checks, SonarCloud issues new and inherited, Copilot and
  reviewer comments, Dependabot and CodeQL alerts, lint and type errors,
  failing tests, known-problems sections) and print the counts before touching
  anything, then fix them in dependency order without changing behavior,
  re-running the relevant check after each group, and report fixed N/N against
  the initial counts. Use when the user says "fix all", "fix a to z", "each and
  every", "fix whatever required", "until all fixed", "all findings", "loose
  ends", or "fix all without breaking anything". Never stops at the first few
  matches, never removes a feature or UI to silence a finding, never reports
  "fixed the issues" without numerator and denominator, and never adds tests,
  docs or refactors that were not asked for.
---

# fix-all

"fix all" is a common opening phrase and the most common failure is the half
sweep: the agent fixes the first page or the first few findings and stops,
and the user comes back with "scan each and every page, not just 1 and 2" or
"I still see a lot of findings in the PR, old and new, fix each and every one".
This skill owns the loop.

## Read first

- Your user-level honesty rules: for sweep/audit tasks, enumerate the full
  match set first, then report progress against that count
- Stale snapshot lists: re-derive the worklist from live data before each
  chunk; a script's own "0 remaining" is not proof
- Don't-remove-unasked: existing UI, content and features stay
- Repo `CLAUDE.md` for the test, lint and build commands that count as checks
  here

## Step 1: enumerate, print, do not touch

Collect every source that applies to the repo or PR and print one table
before any edit. A source with zero findings is still a row.

| Source | How to enumerate |
| --- | --- |
| CI checks | `gh pr checks <n>` or `gh run list --branch <b> --limit 5`; failing job logs via `gh run view <id> --log-failed` |
| SonarCloud | PR check details link, or the SonarCloud API for the project key; count by rule and severity, new vs inherited |
| Review comments | `gh api repos/<r>/pulls/<n>/comments` and `gh api repos/<r>/pulls/<n>/reviews`; Copilot and human, unresolved only |
| Dependabot | `gh api repos/<r>/dependabot/alerts?state=open` |
| CodeQL | `gh api repos/<r>/code-scanning/alerts?state=open` |
| Lint and type | the repo's own scripts (`pnpm lint`, `pnpm type-check`, `ruff check .`, `uv run mypy`); count errors, not files |
| Tests | the repo's own test command; count failing tests |
| Known problems | any `current_problems`, `Known issues` or `TODO` section the user pointed at |

```
| source | count | scope |
| CI checks | 2 failing | build, python |
| SonarCloud | 47 (44 new, 3 inherited) | S3776 x12, S1854 x9, ... |
| review comments | 6 unresolved | Copilot 4, human 2 |
| Dependabot | 0 | |
| CodeQL | 1 | js/incomplete-sanitization |
| lint + type | 13 | eslint 9, tsc 4 |
| tests | 0 failing | 59 pass |
TOTAL 69
```

## Step 2: fix in dependency order

Build-breaking first, then tests, then lint and type, then security alerts,
then quality findings, then review comments. After each group re-run only the
check that group affects and record the new count. Rules while fixing:

- Behavior-preserving. A finding is fixed by correcting the code, never by
  deleting the feature, hiding the UI, downgrading the rule, adding
  `eslint-disable`, `# noqa`, `NOSONAR`, or marking won't-fix in a dashboard.
- Prod-aware. When the user says it is a production environment and to be
  careful, no data migrations and no schema changes inside the sweep; list
  them separately.
- Same branch, same PR. One work stream per PR; do not open a second PR to
  hold the fixes.
- Two failed attempts at one finding: stop iterating on it, list the finding
  with what was tried, move on. Report it in the leftover list.
- Re-derive before each group: the initial counts are a baseline, not the
  worklist. Query the source again so findings that appeared since are caught.

## Step 3: report against the baseline

```
| source | before | after | fixed | left |
| CI checks | 2 | 0 | 2/2 | - |
| SonarCloud | 47 | 3 | 44/47 | S3776 in legacy/parser.ts x3 (complexity split would change behavior; listed for review) |
| review comments | 6 | 0 | 6/6 | - |
| CodeQL | 1 | 0 | 1/1 | - |
| lint + type | 13 | 0 | 13/13 | - |
TOTAL 69 -> 3, fixed 66/69

verified by: <the exact commands re-run and their final output line>
not done on purpose: <features not asked for, tests not asked for>
```

Then, only if the message asked for it, hand to `ship` ("fix all and merge",
"push and create PR"). Otherwise stop with the branch pushed and the receipt.

## Must not

- Never stop before the enumeration table is complete, and never fix before
  printing it.
- Never remove existing UI, content, footers, credits or features to make a
  finding disappear.
- Never report a fix without the before and after counts from a re-run check.
- Never add tests, docs, refactors or "while I was here" changes that were not
  asked for; list them as suggestions at the end if worth it.
- Never silence a rule to reach zero.
- Never run when the user said to skip the quality gates and focus on the
  feature (for example "not sonar, just focus on the UI"); that message
  suspends the gates for the session.

## Non-goals

Deep whole-repo analysis with a report and no edits is `repo-audit`. A Sonar
only sweep with rule-by-rule reporting is `sonar-sweep`, which this skill calls
for the SonarCloud row. Merging is `ship`. Prod verification is `prod-check`.
