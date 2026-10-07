---
name: upstream-pr-prep
description: >-
  Pre-flight check before submitting an upstream PR. Use when the user is
  about to push to a fork and open a PR against upstream.
disable-model-invocation: true
allowed-tools: Read Bash(git:*) Bash(gh pr:*) Bash(gh api:*) Bash(cat:*)
---

# upstream-pr-prep

## When to use

- The user is in a fork checkout and about to open a PR to upstream.
- The user says "ready to PR upstream", "is this PR-ready".

## Steps

1. **Read upstream `CONTRIBUTING.md`.** Note CLA, commit style, base branch, PR template, testing requirements.
2. **Read 3-5 recently merged PRs.** Match their tone, commit granularity, PR body shape.
3. **Check quality bar (7+/10)** per the `vet` mode reference. Is this self-promo? Docstring-only? Trivial typo? If yes, STOP.
4. **Check scope discipline.** Is this PR narrow? Any drive-by formatting to strip?
5. **Check tests.** Match upstream test patterns exactly (framework, fixtures, markers).
6. **Check commits.** Squash/reword to match upstream style. No `Co-Authored-By` unless upstream asks for it.
7. **Sync with upstream.** `git fetch upstream`, then `git rebase upstream/<base-branch>` (one command per line).
8. **Fill the PR template verbatim** if one exists; otherwise use the Problem / Root cause / Fix / Test anatomy.
9. **Report readiness**: green-light or list of blockers.

## Hard rule

**NEVER comment on upstream PRs without explicit permission from the user.** Rebasing own fork is autonomous. Commenting is not.

## Output

```
Upstream: <repo>
Quality bar: <pass/fail + reason>
Scope: <narrow/wide + notes>
Tests: <match/mismatch>
Commits: <clean/needs-squash>
Rebase: <up-to-date/behind-by-N>
PR template: <filled/missing/N-A>
Ready: <yes/no>
Blockers: <list or "none">
```
