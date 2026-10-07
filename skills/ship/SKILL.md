---
name: ship
description: >-
  Land the current work on one of your own repos end to end. Stage by name,
  conventional commit, push, open or update the single PR for this work stream,
  wait for checks, merge only when every gate is green, delete the branch, and
  hand off to prod-check when the repo deploys. Use when the user says "merge
  it", "push and create PR", "if all green merge", "ship it", "open PR to
  main", "merge all", "create PR once done", "delete stale branches", or "push
  it". Never merges red, never force-pushes, never opens a second PR for the
  same branch, never merges a dependency PR whose lockfile did not change with
  its manifest. Own repos only; forks go through the oss skill.
---

# ship

"merge it" is one of the most common bare messages a user sends, and the flow
behind it (commit, push, one PR, wait, merge, clean up, check the deploy) is
easy to get subtly wrong. This skill owns it end to end, gated.

## Read first

- Your user-level rules (git, secrets, honesty and verification)
- The workspace or repo git-workflow doc, if one exists
- `STATUS.md` in the workspace root, if present (which PRs are already open
  for this repo)
- Any protected-branch list in the brain (`brain recall protected branch`):
  branches that workflows write to (e.g. a profile repo's generated-output
  branch) must never be deleted or retargeted

## Gates, in order

Every gate must pass before merge. Report which one failed and stop there.

| Gate | Check | Why |
| --- | --- | --- |
| G1 branch | current branch is not `main`; if it is, branch first (`feat/`, `fix/`, `chore/`) | never commit on main |
| G2 one PR | `gh pr list --head <branch>`; if a PR exists, push to it, never open a second | one PR per work stream |
| G3 checks | `gh pr checks <n> --watch`, every check pass; `mergeStateStatus == CLEAN` | green CI is the merge authority |
| G4 lockfile | if `package.json`, `pyproject.toml`, `requirements*.txt` or `Cargo.toml` changed, the matching lockfile changed in the same PR | the stale-lockfile trap: GitHub reports MERGEABLE when there is no textual conflict, not when the lockfile is consistent with the manifest |
| G5 security | no open Dependabot or code-scanning alert introduced by this PR; `renovate/artifacts` check not failing | never merge with unresolved security findings |
| G6 hooks | no `--no-verify`, no force-push, no amend of a pushed commit | hard rules |

## Procedure

1. Identify scope: repo, branch, what changed (`git status --porcelain`,
   `git diff --stat origin/main...HEAD`). If nothing changed and no PR exists,
   say so and stop.
2. G1. Then stage by name only: `git add <file> <file>`; never `-A` or `.`.
   Check nothing sensitive is staged (`.env*`, `.mcp.json`, tokens).
3. Commit: conventional, lowercase, imperative, one line, no trailers, no
   dash characters. `fix(deps): bump next to 16.3.5 for two critical rce advisories`.
4. Push with an explicit refspec: `git push -u origin <branch>:<branch>`. A
   branch created from `origin/main` tracks main, so a bare `git push` can
   target main. Confirm the branch name in the output.
5. G2. Create or update the PR with `gh pr create --base main --head <branch>
   --title ... --body-file <path>` (a heredoc piped into `gh` can hang on some
   shells; always `--body-file`). Body: what and why, the diff scope, what was
   verified and what was not.
6. G3. `gh pr checks <n> --watch`. On failure read the log
   (`gh run view <id> --log-failed`), fix on the same branch, push, repeat.
   Never mark a check as skipped to get green.
7. G4 and G5. Run the lockfile and security checks explicitly; print the
   result of each.
8. Merge: `gh pr merge <n> --squash --delete-branch`. Confirm with
   `gh pr view <n> --json state,mergedAt,mergeCommit`; `mergedAt` non-null is
   the proof, not the command's exit code.
9. Local cleanup: `git checkout main`, `git pull --ff-only`,
   `git branch -D <branch>`, `git fetch --prune`.
10. Deploy hand-off: if the repo has a deploy target (repo `CLAUDE.md` or a
    deployments doc), run `prod-check` and include its result. "Merged" is
    not "deployed".
11. Update `STATUS.md` if the PR was listed there.

## "merge all"

Enumerate first: `gh pr list --author @me --state open` across the repos in
question, print the count, then apply gates G3 to G5 to each PR and merge the
ones that pass. Report per PR. Bot PRs (Renovate, Dependabot) follow the same
gates; a failing `renovate/artifacts` check means the lockfile was not
regenerated and the PR does not merge. Major version bumps are deferred and
flagged, never merged in a sweep.

## Output

```
| repo | PR | gates | result | proof |
| owner/repo | #N (url) | G1..G6 pass | merged 2026-09-22T11:40:16Z | mergeCommit abcd1234 |
| owner/repo | #M (url) | G4 FAIL | not merged: lockfile pins js-yaml 4.3.1 | sha identical to main |

deploy: <prod-check result or "no deploy target">
branches deleted: remote <branch>, local <branch>
```

## Must not

- Never force-push to `main`, amend a published commit, or pass `--no-verify`.
- Never enable auto-merge; merge on green, not on a timer.
- Never merge with a red check, an `UNSTABLE` or `BLOCKED` merge state, or an
  open security finding.
- Never open a second PR for a branch that already has one.
- Never run this on a fork of someone else's repo; that is the `oss` skill,
  and commenting on upstream PRs needs the user's explicit permission.
- Never claim "merged" or "deployed" without the API field or the live URL that
  proves it.
- Never write an em or en dash character in commit messages or PR bodies.

## Non-goals

No code review (that is `code-review`), no test writing, no release tagging
(release-please owns that where configured), no changelog editing unless the
repo's convention requires one for the change and the user asked for it.
