---
name: oss
description: >-
  Open-source router for the user's upstream work. Status of every open
  upstream PR with rebases of own-fork branches, fork cleanup once a fork's
  PRs are all merged or closed, vetting an idea against the 7/10 quality bar,
  finding contributions, and prepping a PR to the target repo's conventions.
  Use when the user says "open source", "OSS", "status of my open source",
  "rebase all open PRs", "delete this fork", "what maintainer asked", "is
  this worth contributing", "prep this PR for upstream", or runs /oss
  [status|vet|prep|find]. Never comments on an upstream PR without the
  user's explicit permission; find respects any contribution pause the user
  has recorded.
argument-hint: "[status|find|vet|prep]"
---

# oss

One router for upstream contribution work. Pick the mode; read ONLY the matching reference, then follow it.

| Mode | Trigger | Reference |
|------|---------|-----------|
| `find` | "find contributions", hunt for issues matching skills | [references/find-contributions.md](references/find-contributions.md) |
| `vet` | "is this worth a PR?", judge an idea against the 7+/10 bar | [references/meaningful-oss-contribution.md](references/meaningful-oss-contribution.md) |
| `prep` | "prep upstream PR", match style/template before submitting | [references/upstream-pr-prep.md](references/upstream-pr-prep.md) |

Optional gate before `find` mode: if the user has recorded a contribution pause (`brain recall oss pause`), do NO new upstream PR hunting unless they explicitly ask in this session. `vet` and `prep` are always available for work the user initiates.

Standing rules (all modes):
- Quality bar is 7+/10: real problems, live code paths, no self-promo list adds, no bundled fixes.
- Trace the live entry point + read CONTRIBUTING for the base branch before writing anything. Patching a dead duplicate of the code, or targeting `main` when the project merges into `dev`, gets a PR closed.
- Never comment on upstream PRs without explicit permission.

## status mode and fork cleanup

Status and cleanup come up far more often than find or prep.

- `/oss status`: list every open upstream PR authored by the user with
  age, last maintainer activity and CI state (`gh search prs --author @me
  --state open`), then rebase any own-fork branch that is behind
  (`--force-with-lease` on the fork branch only). Never comment upstream; a
  maintainer question is reported to the user, not answered.
- Fork cleanup: a fork whose every PR is merged or closed (verify each with
  `merged_at`, both search and per-PR API) is deleted after backing up unmerged
  diffs to a local patch backup dir (for example `~/branch-backup/fork-patches/`).
  Needs the `delete_repo` scope. Deleting the fork does not remove the PR
  record upstream.
- A recorded contribution pause gates `find` only; `status` and cleanup are
  always allowed.
