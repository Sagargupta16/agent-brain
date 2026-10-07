---
name: github-pr-checks-stall-causes
description: "A PR whose required checks never go green is often GitHub-side -- first-time fork runs parked at action_required, or a re-run replaying a stale merge ref"
type: reference
source: "observed 2026-09-18 to 2026-09-30 on a public awesome-list repo with auto-merge and required checks"
created: 2026-09-30
modified: 2026-10-07
status: active
visibility: public
---

Three GitHub behaviours each made a correct pull request look broken. None of them is a code problem, so check them before editing anything.

**Why:** PRs sat with auto-merge armed and required checks missing; another kept failing after the validator fix had already merged; an issue-form label silently never applied.

**How to apply:**

- **Required checks absent, run conclusion `action_required`.** A fork PR from a first-time contributor is waiting for workflow approval, and auto-merge waits forever. Approve each such run on the head SHA with `gh api -X POST repos/O/R/actions/runs/<id>/approve`. The policy lives at `PUT repos/O/R/actions/permissions/fork-pr-contributor-approval`; valid values are `first_time_contributors_new_to_github`, `first_time_contributors`, `all_external_contributors`. There is no `never` (returns 422). The least friction is `first_time_contributors_new_to_github`.
- **Re-running a failed `pull_request` check after the fix merged still fails with the OLD message.** A re-run replays the cached merge ref. Refresh the branch with `gh api -X PUT repos/O/R/pulls/<n>/update-branch` (works on a fork PR when `maintainerCanModify` is true), which starts fresh runs.
- **An issue form `labels:` entry naming a label that does not exist is dropped silently.** Create the label first (`gh label create ...`).
- Does NOT cover PRs opened or merged by `GITHUB_TOKEN`; those are in [[github-token-automation-gotchas]].

Related: [[github-token-automation-gotchas]], [[sonarcloud-gate-fails-on-duplication]].
