---
name: parallel
description: >-
  Fan-out recipe for when the user wants speed through agents. Partitions
  work by unit (page, route group, file lane, repo), gives each agent sole
  write ownership of disjoint files and a bounded prompt with a verify step,
  launches all lanes in one Agent tool call, then runs the gates once and
  reports per lane. Use when the user says "run parallel agents to do things
  fast", "one agent for each page, fix all pages in parallel", "run more
  agents, I don't see much progress", or "strictly use parallel agents".
  Never spawns agents for a single-file task, lets two agents own one file,
  re-runs gates per agent, or commits before integration.
---

# parallel

When progress looks slow, the answer is more lanes, never smaller scope: "run
parallel agents to do things fast", and later "run more agents, I don't see
much progress". This is the scouts -> one synthesizer -> per-file fixers ->
verify shape as a recipe on the Agent tool.

## Read first

- Prior lessons in the brain: `brain recall parallel`, `brain recall
  workflow` (and read the diff yourself; a subagent summary is not the diff)
- The repo's `CLAUDE.md` for the gate command (`pnpm run check`, `uv run pytest`)
  and any worktree rule (for example: worktrees at the repo root, never under
  a nested package such as `frontend/`, or typescript-eslint sees two tsconfig
  roots)

## Procedure

1. Qualify. Count the independent units. One file, or units that all edit the
   same file, means no agents: do it inline and say why in one line. Two or
   more disjoint units means fan out with as many lanes as units; the user
   asked for speed, not a cap.
2. Partition by the natural unit and print the lane table BEFORE launching:

```
| lane | owns (write) | reads | verify | agent |
| pages/budget | frontend/src/pages/budget/** | components/ui/** | render /budget at 375px, no console errors | 1 |
| pages/goals | frontend/src/pages/goals/** | same | render /goals | 2 |
```

   Check disjointness mechanically: `git ls-files <glob>` per lane, then
   `sort | uniq -d` across all lanes must print nothing. A shared file (util,
   type, barrel) gets its own lane that runs FIRST, or one lane owns it and the
   rest treat it read-only.
3. One prompt per lane, same skeleton for all, the user's verbatim ask
   included: the goal in their words; `owns:` list; `read-only:` list; rules:
   no formatting or cleanup outside `owns`, no commit, no typecheck, lint,
   build or test run (those run once, at integration), Edit tool only (CRLF
   repos); the lane's own verify step (render the page, run the one test file,
   hit the one endpoint); return shape:
   `lane | files changed | what changed | verified how | left open`.
4. Launch every lane in ONE message with the Agent tool: `subagent_type`
   `general-purpose` for edits, `Explore` for read-only scouts,
   `run_in_background: true`. Do not poll and narrate; work the shared lane or
   the integration checklist while they run. `isolation: "worktree"` only when
   two lanes must touch the same file, and then integration is a cherry-pick
   per worktree, not a merge.
5. Integrate, once, in this order: `git status --porcelain` and
   `git diff --name-only`; every path maps to exactly one lane's `owns`, or it
   is reverted and that lane re-run with a tighter prompt. Read the full diff
   yourself. Then the repo's gate command one time, plus the test suite. A red
   gate is fixed here in the main loop, not by re-spawning every lane.
6. Report per lane with the agent's return line beside your own verification.
   A lane whose claim you did not check is marked `(unverified)`.
7. Commit only after step 5 passes and only if the same message asked; then
   `ship` (one PR per work stream, never one per lane).

## Output

```
lanes: 6 launched 10:02 | 6 returned by 10:19 | files touched 23 (0 overlaps)

| lane | files | agent said | I verified | open |
| pages/budget | 4 | fixed truncated amount cells, 375px ok | diff read; /budget rendered | none |
| pages/goals | 3 | ... | (unverified: page needs login) | login-gated check |

gate: pnpm run check pass (once) | tests 214/214 (once)
commit: not asked / <sha> via ship
```

## Must not

- Never spawn agents for a single-file or single-unit task; say "one unit,
  doing it inline" and do it.
- Never let two lanes own the same file; a shared file is its own lane or
  read-only to all but one.
- Never run type, lint, build, or tests per agent or per lane; once, at
  integration.
- Never accept "done" from an agent without reading its diff; the summary
  describes intent.
- Never commit, push, or open a PR before the integration pass, and never one
  PR per lane.
- Never let an agent commit, format unrelated files, or edit outside `owns`.
- Never report a lane as verified when the check was the agent's own claim.
- Never chain commands with a double ampersand, in the shell or in a lane
  prompt; one per line.

## Non-goals

Deciding what to fix (`repo-audit` and `fix-all` enumerate the work; this
skill only runs it wide), merging (`ship`), workflow scripts (a
workflow-authoring skill, if installed), per-lane domain rules (design or
clean-code skills, if installed, load inside the lane prompt when relevant).
