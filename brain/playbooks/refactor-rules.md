---
name: refactor-rules
description: "When to refactor and when not to, scope discipline, a safe refactor workflow, transformations ranked by risk, renames, moves, dead code, API surface"
type: playbook
source: "ported from a private multi-repo workspace playbook"
created: 2026-10-07
modified: 2026-10-07
status: active
visibility: public
---

# Refactor Rules

## When to refactor

- **Rule of three** -- extract after the third duplication, not the second.
- **Reading pain** -- you had to re-read a function twice to understand it.
- **Bug-prone spot** -- the same area keeps breaking.
- **Before adding a feature** that would be painful in the current shape.

## When NOT to refactor

- You are fixing a bug. A bug fix is not a refactor invitation.
- You are "just passing through." Leave it cleaner only if it is a one-line cheap change.
- The code is working, untested, and not being touched for a feature.
- No abstractions for single-use code.
- Premature abstraction -- if the second use case is not real yet, wait.

## Scope discipline

When the user says "just fix X":

- Change only what is needed for X.
- No adjacent cleanup.
- No "while I'm here" renames.
- No file reorganization.

When the user grants autonomy ("do it", "go ahead"):

- Still do not scope-creep.
- Fix what was asked. Flag adjacent issues in a follow-up message; do not fix them silently.

## Safe refactor workflow

1. **Tests green before.** If there are no tests, add characterization tests first.
2. **One transformation at a time.** Extract, rename, inline -- commit each.
3. **Tests green after each step.**
4. **Diff review** before shipping -- does the diff match the intent?
5. **Run the feature.** Not just the tests. (See [review-bar.md](review-bar.md).)

## Transformations by risk

### Low risk (just do it)

- Rename a local variable.
- Extract a local constant.
- Extract a small pure function.
- Reorder independent statements.

### Medium risk (tested before)

- Rename a public function or class.
- Extract a module.
- Change a function signature (with all callers updated in the same PR).
- Replace a conditional with polymorphism.

### High risk (plan + explicit approval)

- Change the public API shape.
- Move files across package boundaries.
- Migrate state management (Context -> Zustand, etc.).
- DB schema changes.

## Naming

- A rename is a refactor. Do it in isolation, not bundled with logic changes.
- A rename PR should be 100% renames, 0% behavior change.

## Moves

- git detects a moved file if rename similarity is above 50%. Do not combine a move with content edits.
- Move + edit = one PR for the move, one for the edit.

## Dead code

- Delete commented-out code on sight.
- Unused functions and imports -- delete, let the linter enforce it.
- "Might need this later" -- you won't. Git remembers.

## API surface

- Narrowest possible. Export only what callers need.
- Default to private / module-local. Promote when there is a second user.
- Removing something from a public API is a breaking change -- deprecate first if published.

## Measurement

- If the refactor claims a perf win, benchmark before and after.
- If it claims "readability," get a review. You cannot self-assess.
- If it claims "maintainability," wait for the next feature to validate it.
