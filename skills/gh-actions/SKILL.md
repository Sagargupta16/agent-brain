---
name: gh-actions
description: >-
  GitHub Actions owner for your repos. Reads the failing run's log, diagnoses
  it (expired PAT, pnpm or uv drift, flaky step), patches workflow or code,
  pushes, and watches the re-run to success; also authors scheduled and release
  workflows. Use when the user says "fix CI fails", "why did this workflow
  fail, see and fix", "are all pipelines passed", "write a github action that
  runs a script every day at a random time", "make it so everything is
  automated", or "publish should be automated, why so many steps". Never skips
  a check to force green, stores a secret in a workflow file, or merges on its
  own.
---

# gh-actions

The asks split two ways: "why did this workflow fail, see and fix" (repair)
and "make it so everything is automated" (author). Both end with a green run
the user can click.

## Read first

- Your user-level rules (git, secrets, honesty and verification)
- Any protected-branch list in the brain (`brain recall protected branch`):
  branches that workflows push generated output to
- Your reusable-workflows repo, if you have one: its README (workflow table)
  and the inputs of each reusable workflow. If consumers pin `@main`, a change
  there is a production deploy for every caller
- The repo's own `CLAUDE.md` (CI section, toolchain gotchas)

## Procedure: repair

1. Enumerate before touching:
   `gh run list --repo <owner>/<repo> --limit 20 --json databaseId,name,conclusion,headBranch,event,url`
   and for a PR `gh pr checks <n>`. Print `failing N/M`.
2. Read the log, not the check name: `gh run view <id> --log-failed`. Quote the
   first real error line in the reply.
3. Match the known causes before inventing one:

| Symptom in log | Cause | Fix |
| --- | --- | --- |
| `Bad credentials`, 401 on `gh` or API steps | expired PAT stored as a repo secret | name the secret and the scopes it needs for the user to rotate; never paste a value |
| `ERR_PNPM_BAD_PM_VERSION`, `packageManager` mismatch | pnpm drift between `package.json` and `pnpm/action-setup` | let the setup step read `packageManager`, or align the version |
| `typescript-eslint does not support TS <N>` | TypeScript bumped past the lint plugin's peer range | revert the TS bump, never the lint |
| `No such file` on a `\` path or wrong case | Windows-authored path on a Linux runner | forward slashes, exact case |
| `Node.js 20 actions are deprecated` | old JS action runtime | `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` in `env:`, then bump the action |
| `renovate/artifacts` red | lockfile not regenerated | regenerate on the branch; a manifest bump alone is not a fix |
| green on rerun | flaky step | `gh run rerun <id> --failed` once; flakes twice, fix the step (timeout, retry, cache key) |

4. Patch on the current branch, never on `main`. Prefer replacing a hand-rolled
   job with `uses: <owner>/<reusable-workflows-repo>/.github/workflows/<name>.yml@main`
   when one covers it; keep repo-specific jobs (for example a database
   migrations job).
5. Push, find the run, watch it:
   `gh run list --branch <branch> --limit 1 --json databaseId,url`
   `gh run watch <id> --exit-status`
   `gh run view <id> --json conclusion,updatedAt`
   `conclusion: success` is the proof, not "pushed the fix".
6. Report per run. "if green merge" hands to `ship`; a repo with a deploy target
   hands to `prod-check`, since a green run is not a live site.

## Procedure: author

1. Decide from the repo, ask nothing: `pyproject.toml` -> a Python CI
   workflow, a JS lockfile -> a Node CI workflow (the reusable one if you have
   it), deploy target from the repo `CLAUDE.md` or the deployments doc.
2. Every new workflow gets `permissions:` at the top with the least the jobs
   need (`contents: read` unless it commits), `concurrency` with
   `cancel-in-progress: true`, `timeout-minutes`, `workflow_dispatch` so it
   can be run today, and actions pinned to a full SHA with the version as a
   trailing comment (`actions/checkout@<full-sha> # v5`), a form Renovate and
   Dependabot keep current.
3. Scheduled jobs: cron cannot be random. Off-minute cron (`"17 3 * * *"`,
   never `:00`, which GitHub delays) plus jitter as the first step:
   `sleep $(shuf -i 0-5400 -n 1)`. Say in the reply that GitHub disables a
   schedule after 60 days without repo activity.
4. Publish automation: conventional commits drive release-please
   (`release-please-config.json`, `.release-please-manifest.json`, a
   `release.yml`); never a hand-pushed `v*` tag. Tag-triggered builds call
   the release workflow.
5. A step whose exit code lies (for example a store upload that returns 400
   yet publishes) gets `continue-on-error: true`, a comment saying why, a next
   step that queries the real system and is the blocking one, and an
   `if: always()` report to `$GITHUB_STEP_SUMMARY` that spells out the manual
   recovery. A deploy gated behind a flag states in a comment which repo
   variable flips it live and what to uncomment.
6. Verify: `gh workflow run <file> --ref <branch>`, then step 5 of repair.
   A workflow that has never run is not authored.

## Output

```
| repo | workflow | run | before | cause | after | proof |
| owner/x | ci.yml | 12345 (url) | failure | pnpm 10 vs packageManager 11 | success | run 12346 conclusion=success 2026-09-22T09:14:02Z |

authored: <file> | cron <expr> | permissions <list> | first run <url> success
handoff: ship (merge) / prod-check (deploy) / none
```

## Must not

- Never skip, disable, or `continue-on-error` a failing check to get green; the
  lying-exit-code form is allowed only with the verifying step behind it.
- Never write a token or key into a workflow, a `--body-file`, or the reply;
  secrets stay `${{ secrets.NAME }}` and the reply names them only.
- Never merge; that needs the user's "if green merge" and goes through `ship`.
- Never delete or retarget a branch a workflow writes to (a `target_branch`
  or publish branch); when such a workflow is red, fix the step, keep the
  branch.
- Never edit the reusable-workflows repo as a drive-by from a consumer; it
  gets its own PR and one consumer CI run after merge.
- Never chain commands with a double ampersand, in the shell or in a line you
  hand the user for PowerShell 5.1; one command per line.
- No `--no-verify`, no force-push, no amend of a pushed commit.

## Non-goals

Merging (`ship`), live deploy verification (`prod-check`), SonarCloud findings
(`sonar-sweep`), Renovate PR triage (a repo-ops skill, if installed).
