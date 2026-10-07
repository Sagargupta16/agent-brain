---
name: git-workflow
description: "Branch model, conventional commits, one-commit-per-concern, staging, pre-push checks, rebase vs merge, PR follow-up, and dangerous commands"
type: playbook
source: "ported from a private multi-repo workspace playbook"
created: 2026-10-07
modified: 2026-10-07
status: active
visibility: public
---

# Git Workflow

## Branch model

- **`main`** is protected. No direct commits for any non-trivial change. New repos: `git init -b main`.
- **Feature branches** off `main`: `feat/<topic>`, `fix/<topic>`, `chore/<topic>`, `docs/<topic>`, `refactor/<topic>`.
- **Upstream forks** -- branch names match upstream's convention.

## Commit style

**Conventional commits**:

```
feat: add sankey diagram to the dashboard
fix: handle empty csv in parser
refactor: extract tax calc into pure fn
docs: update data schema
test: cover edge case in auth middleware
chore: bump deps
```

The body is optional -- use it for the *why* when it is not obvious from the subject.

## Commit shape for multi-concern sessions

When a single session touches several concerns (fix + feat + docs + chore), split into N logical commits -- one per concern -- before pushing. Do not bundle.

Example: a plugin repo release shipped as 5 commits instead of 1:

1. `docs:` a leftover uncommitted docs edit
2. `fix:` validator CRLF bug (an isolated fix benefits from its own commit for future bisect)
3. `docs:` governance files (SECURITY, PR template, issue templates, versioning policy)
4. `feat:` the new feature
5. `chore:` release (version bumps, CHANGELOG, doc sync)

Benefits: clean revert granularity, readable `git log`, each PR description writes itself, bisect pinpoints the real regression.

## Staging

- Stage by name: `git add path/to/file1 path/to/file2` (blanket staging once caught a `.env`).
- Verify with `git status` before commit.

## Before push

- [ ] `git status` -- only expected files staged.
- [ ] `git log` -- commits look clean.
- [ ] `git branch` -- correct branch.
- [ ] Tests pass.
- [ ] Hooks run (no `--no-verify`).

## Push

- Own repos: push to a feature branch, open a PR via `gh pr create`.
- Upstream forks: push to your fork's branch, open a PR against upstream.
- A branch created with `git switch -c <b> origin/main` tracks `origin/main`, so a bare `git push` targets main. Push new branches with an explicit refspec: `git push -u origin <b>:<b>`.
- Never force-push to `main`.
- Force-pushing your own feature branch after a rebase is fine.
- Never force-push to someone else's branch.

## Rebase vs merge

- **Rebase feature onto main** before merging, to keep history linear.
- **Merge** when integrating long-running branches (rare).
- **Squash-merge** on GitHub for noisy feature branches.

## Amending

- Amend unpublished commits freely.
- **Never amend published commits.** Create a new commit.

## Signing

- SSH signing works well: `commit.gpgsign=true`, `gpg.format=ssh`, `user.signingkey` pointing at your public key, and the key registered as a Signing Key on GitHub.

## GitHub CLI

- Prefer `gh` over the web UI for PR operations.
- `gh api` for anything not exposed by `gh pr` / `gh issue`.
- `gh pr create`, `gh pr view`, `gh pr checks`, `gh pr merge`.

## When a PR comes back with changes

1. Read comments first -- `gh api repos/{owner}/{repo}/issues/{num}/comments` and `.../pulls/{num}/comments`.
2. Check merge readiness -- `gh api repos/{owner}/{repo}/pulls/{num} --jq '{mergeable, mergeable_state, draft}'`.
3. Check how far behind -- `gh api repos/{owner}/{repo}/compare/{base}...{head} --jq '{behind_by, ahead_by}'`.
4. Rebase + push to the same branch (one PR per work stream).
5. Update your status tracking.

## Deleting forks

- Verify **zero open PRs** from the fork before deleting.

## CRLF on Windows

Line-ending flips inflate dirty counts. Do not commit the flip -- `git checkout -- <file>` if the diff is pure CRLF. See the learning `git-on-windows-gotchas`.

## Dangerous commands (never without explicit confirmation)

- `git reset --hard`
- `git push --force` to `main`
- `git clean -fdx`
- `git filter-branch` / `git filter-repo`
- interactive rebase on published commits
