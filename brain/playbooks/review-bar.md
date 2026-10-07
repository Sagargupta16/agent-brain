---
name: review-bar
description: "Checklist before claiming work is done or asking for review -- pre-claim verification, self-review, security, performance, upstream PR extras"
type: playbook
source: "ported from a private multi-repo workspace playbook"
created: 2026-10-07
modified: 2026-10-07
status: active
visibility: public
---

# Review Bar

The checklist before claiming work is done or asking for PR review.

## Pre-claim verification (non-negotiable)

- [ ] **Backend changes** -- server runs, affected endpoints hit.
- [ ] **Frontend changes** -- dev server starts, feature works in the browser (golden path + one edge case).
- [ ] **All code changes** -- tests pass, types check, build succeeds.
- [ ] **Git operations** -- `git status` + `git log` confirm the expected state.
- [ ] Never claim "done" on types/lint alone. Run the actual feature.

## Code review self-check

Before pushing or asking for review:

- [ ] Does each commit do one thing?
- [ ] Does the diff match the intent described in the PR/commit message?
- [ ] No debug `print` / `console.log` / `debugger;` leaked in.
- [ ] No commented-out code.
- [ ] No `TODO` without a date or issue.
- [ ] No `any` in TS without justification.
- [ ] No `except: pass` in Python.
- [ ] New code has tests. A bug fix has a regression test.
- [ ] Public API changes documented.
- [ ] Sibling files updated (CHANGELOG, README, agent instructions, status docs) if behavior, commands or architecture changed.

## Security quick-check

- [ ] No secrets, tokens, keys or passwords in the diff.
- [ ] No `.env` staged.
- [ ] User input validated at entry.
- [ ] No string-concatenated SQL.
- [ ] CORS not `*` in prod code.
- [ ] Passwords hashed with bcrypt/argon2, not MD5/SHA.

## Perf quick-check

- [ ] No N+1 query in new DB code.
- [ ] No synchronous I/O in hot paths.
- [ ] No unbounded lists or recursion.
- [ ] Large lists virtualized in the UI.

## Upstream (OSS) PR extras

- [ ] Upstream `CONTRIBUTING` read.
- [ ] Commit style matches upstream.
- [ ] PR template filled, CLA signed if required.
- [ ] Tests match upstream patterns exactly.
- [ ] 7+/10 quality bar -- is this actually valuable, or self-promo? See the learning `oss-pr-quality-bar`.

## Quality bar

**7+/10 only.** Close your own PRs that are:

- Self-promo (awesome-list adds with no substance).
- Docstring-only with no behavior change.
- Trivial typo fixes upstream (unless asked).
- Code that works but does not carry its weight.

## If something is off

- Flag it clearly. Do not hide it under "ready to merge."
- Fix before claiming -- never "done-ish."
- Do not merge with unresolved security findings.
