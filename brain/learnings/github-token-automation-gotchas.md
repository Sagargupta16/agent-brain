---
name: github-token-automation-gotchas
description: "PRs opened or merged with GITHUB_TOKEN start no workflow runs and skip closing keywords; labeled issue forms double-fire; how a form-to-PR self-merging bot works around them"
type: reference
source: "observed 2026-09-26 building an issue-form to auto-merged-PR pipeline plus an hourly GitHub Pages rebuild"
created: 2026-09-26
modified: 2026-10-07
status: active
visibility: public
---

These GitHub rules broke the naive version of a "submit a form, bot opens a PR, PR auto-merges, site rebuilds" pipeline. They apply to any repo that automates with `GITHUB_TOKEN`.

- **A PR opened with `GITHUB_TOKEN` starts no `pull_request` workflow runs**, so required checks never report and auto-merge waits forever. Fix: `gh workflow run <wf> --ref <branch>` for each check workflow. The check runs land on the branch head, which is the PR head, and satisfy required checks by name. Each dispatched workflow needs a `workflow_dispatch` trigger and a fallback for every `github.event.pull_request.*` expression.
- **A merge by auto-merge on `GITHUB_TOKEN` starts no `push` run** and does NOT apply "Closes #N". Give downstream jobs (like a Pages build) a schedule, and close the linked issues from a sweep job.
- **An issue created from a form with a label fires `opened` AND `labeled`.** Triggering on both runs the workflow twice and posts duplicate comments. Trigger on one.
- **The repo setting "Allow GitHub Actions to create and approve pull requests" must be on** for the bot to open PRs.
- **Sonar rule S8233 fails the gate on workflow-level write permissions.** Put `permissions: {}` at the top of the workflow and grant per job.

**How to apply:** verify the whole loop live once (form submitted, PR opened, checks green, merged, site updated) before calling the pipeline done.

Related: [[github-pr-checks-stall-causes]], [[github-marketplace-action-publishing]].
