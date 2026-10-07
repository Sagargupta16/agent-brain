---
name: sonar-sweep
description: >-
  Pull the open SonarCloud findings for a repo or PR via its API, print the
  count by rule and severity first, fix them in place without behavior change
  (complexity splits, nested ternaries, unused imports), run the repo's lint
  and type lane once, and report fixed N/N with false positives listed by rule
  id. Use when the user says "fix all sonarcloud findings", "fix the 47 new
  sonarcloud issues", "sonarcloud still failing, fix it", "sonar findings on
  the PR, fix and merge", or "also fix any sonarcloud issues". Never marks an
  issue won't-fix or disables a rule to drop the count, and stands down on
  "not sonar, focus on the feature".
---

# sonar-sweep

The ask has one shape: a SonarCloud number the user saw on the PR ("fix the 47
new sonarcloud issues") and an order to make it zero without breaking
anything. This skill does it with `gh` plus the SonarCloud API, no plugin
needed.

## Read first

- Your user-level rules (honesty and verification, editing files)
- Feature vs gate: quality gates are a cleanup phase paid back in bulk, not a
  build phase. On a feature turn where the user has not named Sonar, this
  skill does not run.
- The repo's `sonar-project.properties` or `.sonarcloud.properties` (automatic
  analysis vs a scan step in a workflow) and its `CLAUDE.md` quality rules

## Procedure

1. Resolve the project key, in order: `sonar.projectKey` in the properties file;
   the SonarCloud check run on the PR head
   (`gh api repos/<owner>/<repo>/commits/<sha>/check-runs --jq '.check_runs[] | select(.name | test("Sonar")) | .details_url'`,
   the URL carries `id=<key>` and `pullRequest=<n>`); else `<owner>_<repo>`,
   the default for GitHub-imported projects. The organization key is usually
   the lowercased GitHub owner.
2. Enumerate, print, then edit. Public projects need no token; a private one
   takes `-H "Authorization: Bearer $SONAR_TOKEN"` with the value never echoed:
   `curl -s "https://sonarcloud.io/api/issues/search?componentKeys=<key>&resolved=false&ps=500&facets=rules,severities,types"`
   Add `&pullRequest=<n>` for PR-new issues; omit it for `main`. Then the gate:
   `curl -s "https://sonarcloud.io/api/qualitygates/project_status?projectKey=<key>&pullRequest=<n>"`
   Print the total, count per rule id, count per severity, and the failing gate
   condition. That total is the denominator for the rest of the session. A gate
   can fail with 0 issues: check `new_duplicated_lines_density` too (copied test
   fixtures count as duplication).
3. Work by rule id, not by file: one rule has one mechanical fix, applied across
   every occurrence before the next rule.

| Rule | Fix that keeps behavior |
| --- | --- |
| S3776 cognitive complexity | extract the deepest branch into a named function; same inputs, same return |
| S3358 nested ternary | `if`/`else` or a small lookup map |
| S1128 unused import (ruff F401) | remove; then run the type lane, the import may have carried a side effect |
| S1192 duplicated string | one `const` at module top with the identical literal |
| S6582 optional chain, S6606 nullish | rewrite; keep falsy-vs-nullish semantics identical, check the tests around it |
| S1481 unused local, S1854 dead store | delete the store; if it fed a log line, keep the log |
| S1186 empty function, S2486 ignored exception | narrow the catch to the expected error and handle or rethrow; never `pass` |
| S8476 forged client request | build with `URL`, pin the origin |

4. Preserve line endings (no `sed -i` on CRLF repos), no formatter over
   untouched files. Every changed line traces to an issue in the list; if not,
   revert it.
5. Verify once at the end, not per file: the repo's own lane (a single
   `pnpm run check` if it has one; else `pnpm run lint` then
   `pnpm run typecheck`, or `uv run ruff check .` then `uv run mypy`) plus the
   tests covering the touched files. A red lane means step 4 changed behavior;
   fix that first.
6. Push to the existing PR branch (never a second PR), wait for the SonarCloud
   check (`gh pr checks <n> --watch`), re-run step 2 with the same parameters.
   The API total is the proof: `47 -> 0` from `issues/search`, not from the diff.
7. Whatever remains is a false positive or out of scope. List each by rule id,
   `file:line`, and one line why. Do not resolve it in SonarCloud; the user
   decides.
8. If the same message said "merge it", hand to `ship` with the count table.

## Output

```
| scope | before | fixed | left | proof |
| PR #N new | 47 | 47 | 0 | issues/search total=0 at 2026-09-22T10:02:11Z |
| main inherited | 12 | 9 | 3 | issues/search total=3 |

by rule: S3776 14/14, S3358 9/9, S1192 20/20, S6582 4/4
false positives (left unresolved in SonarCloud): S1192 src/x.ts:41 test fixture literal
gate: passed / failed on <condition>
lane: pnpm run check pass | tests 212/212
```

## Must not

- Never mark an issue won't-fix, false positive, or resolved in SonarCloud; the
  count drops only because code changed.
- Never disable or exclude a rule in `sonar-project.properties`,
  `.sonarcloud.properties`, ESLint, or ruff config; never add `// NOSONAR` or
  `# noqa` to make a finding vanish.
- Never remove a feature, a UI element, a test, or a log line to satisfy a rule.
- Never reformat, re-order imports, or "clean up" a file with no finding.
- Never report "fixed the sonar issues"; only `fixed N/M` with the API total.
- Never run on a feature turn: "not sonar, just focus on the UI" ends this
  skill at once; note the count for later.
- Never echo `SONAR_TOKEN` or any credential value in a command or the reply.
- Never chain commands with a double ampersand; one per line.

## Non-goals

Other red CI checks (`gh-actions`), reviewer and Copilot comments and
Dependabot alerts (`fix-all`, which calls this for its Sonar lane), merging
(`ship`), structural refactors beyond the finding (a clean-code skill, if
installed).
