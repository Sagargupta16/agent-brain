---
name: ideate
description: >-
  Structured brainstorming for one of the user's repos or a new project.
  Inventory what exists (README, pages, TODO.md, issues, commits) so nothing
  is restated, then a ranked table of 10 to 20 concrete ideas with the gap
  each fills, effort S/M/L, the user served, unique vs table stakes, a reuse
  pointer into the user's own repos, and a 3-step next phase; accepted ideas
  go to TODO.md in its section format. Use when the user says "any more
  suggestions?", "new project idea, an app like X but not X", "among our
  apps which should get a mobile app?", "make it unique", or "whats next".
  Never starts implementing; ideas only until the user says do it.
---

# ideate

Some asks want ideas rather than code: "what more features can we add to make
this unique?", "any more suggestions?", "new project idea, an app like X but
not X", "among our apps which should get a mobile app?". The usual failures:
ideas that already exist in the repo, generic SaaS padding, and an agent that
starts building. This skill ends at the table.

## Read first

- The repo: `README.md`, `CHANGELOG.md`, `TODO.md` if present, the pages or
  routes directory (`frontend/src/pages`, `src/app`, `src/routes`, or the
  FastAPI `routers/`), `gh issue list --state open --limit 50`,
  `git log --oneline -20`
- The workspace `TODO.md` if the user keeps one: the backlog and its section
  format
- Build vs install vs reuse: existing own code beats an installed tool beats
  new code; `brain recall reuse` and `brain recall stack` for prior decisions
- A design skill, if installed, when the ideas are UI
- Prior-art and competitor lookups go through web fetch or a search tool,
  never a browser automation tool

## Procedure

1. Scope: which repo, or "new project". An ambiguous name (two repos could
   match) gets one question; otherwise state the assumption and go.
2. Inventory, and print the counts: N pages or routes, M open issues, K TODO
   items, last release date, the feature list from the README. Every idea is
   checked against this list before it is written down.
3. Users: name the one to three user types the repo actually serves, from the
   README, not invented personas. Each idea maps to one.
4. Generate 10 to 20 ideas. For each: one line what, one line why tied to a gap
   from step 2 (a missing page, an open issue, a TODO, a competitor feature
   found in step 6), effort (S under one evening, M a weekend, L multi-week),
   user served, reuse pointer (which of the user's repos already has the
   piece: a file parser, a chart component, an API client, a media store, an
   MCP server), and when the user said `make it unique`, a tag: unique (no
   tool found in step 6 does it) or table stakes (expected, not
   differentiating).
5. Rank: `score = impact (1 to 3) * reach (1 to 3) / effort (S 1, M 2, L 3)`;
   sort descending; ties broken by reuse (more reuse first). Print the score.
6. Prior art for `unique` claims and for new project ideas: `gh search repos
   "<two keywords>" --sort stars --limit 5` plus one fetch of the obvious
   competitor. "Never made before" is written only when the search came back
   empty or clearly different, with the query quoted.
7. New project ideas: constrain to the user's stack, hosting and audience
   (read them from the workspace `CLAUDE.md` or `brain recall stack`; for
   example React + Vite or FastAPI, Expo for mobile, a static host or a
   serverless platform, mobile-first users). 5 to 10 ideas, same columns plus
   a prior-art column.
8. "Which of our apps should get X": a decision table across the candidates
   (backend reusable, data model ready, daily-use motivation, needs native
   features, effort), then one recommendation with its tradeoff. If `TODO.md`
   already holds a parked entry for one candidate, cite it rather than
   re-deriving it.
9. Next phase: three steps the user could answer with `do it`, each with the
   check that proves it done (a route exists, a test passes, a URL responds).
10. Persist only on acceptance (`yes`, `1 3 5`, `add these`, `remember`):
    append to the repo `TODO.md` if it exists, else to the workspace
    `TODO.md`, one section per idea, separated by `---`:

    ```
    ## <Idea title>
    **Status**: Planned | Parked (<YYYY-MM-DD>) | Idea (<YYYY-MM-DD>)

    - <what>
    - <why, effort, user>
    - Decided <YYYY-MM-DD>: <the user's words on why it is in or out>
    ```

    Re-read the appended block and report its line range. No commit; `ship`
    does that when asked.
11. Stop. `do it`, `do 1 3` or "keep making the project better" hands the
    picked rows to normal coding on one branch; this skill's job ended at the
    table.

## Output

```
inventory: 26 pages, 4 open issues, 6 TODO items, last release <YYYY-MM-DD>

| # | idea | gap it fills | effort | user | unique or table | reuse from | score |
| 1 | ... | open issue, no export | S | self-hosting user | table | <repo>/src/export.ts | 9.0 |

next phase: 1. <step> (check: ...) 2. ... 3. ...
appended: <path> lines a to b | nothing yet, waiting for the user's pick
```

## Must not

- Never start implementing: no branch, no scaffold, no file edits outside
  TODO.md, until the user says `do it` or names rows.
- Never pad with generic SaaS features (dark mode, notifications, "AI chatbot",
  gamification) unless tied to a gap in this repo's data or users.
- Never restate a feature that exists; the inventory check in step 2 is the
  gate, and a restated feature is a defect.
- Never write "unique" or "never made before" without the step 6 query quoted.
- Never exceed 20 ideas or offer three options where the user asked which;
  one recommendation with the tradeoff.
- Never rewrite or delete existing TODO.md sections; append only, and flip a
  Status only when the user says decided.
- Never create a repo or commit (`ship`) unless asked.

## Non-goals

Building the idea (normal coding, then `ship`), scaffolding a repo, UI
critique (a design skill, if installed), bug audits (`code-review`,
`repo-audit`), cited research reports (a research skill, if installed).
