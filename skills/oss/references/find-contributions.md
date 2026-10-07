---
name: find-contributions
description: >-
  Find open-source contribution opportunities matching the user's skill set,
  filtered by the quality bar (7+/10). Use when the user says "find
  contributions", "OSS opportunities", or runs /oss find.
allowed-tools: Bash(gh search:*) Bash(gh api:*)
---

# find-contributions

## Task

If `$ARGUMENTS` names a specific repo, search only that repo. Otherwise search broadly.

1. **Scoped mode** (`$ARGUMENTS` = repo): find issues labeled `good first issue` or `help wanted`, recent unassigned issues, existing merged PRs for style, and read CONTRIBUTING.md.
2. **Broad mode** (no args): search across the user's strong-fit topics (read them from `brain recall oss skills`, or ask once and `brain remember` the answer; for example Terraform, Python, FastAPI, React, TypeScript, AWS, Docker).
   - `gh search issues "good first issue" language:python stars:>100 state:open`
   - Repeat for each language in the user's fit list.
3. For every candidate issue, assess fit against the user's list:
   - **Strong**: languages and stacks they ship daily
   - **Medium**: languages they are learning
   - **Avoid**: languages they have said they will not work in
4. Filter out issues that already have open PRs from others (`gh pr list --state open --search "<issue-ref>"`).
5. Apply the 7+/10 quality bar -- see the `vet` mode reference. Skip self-promo awesome-list adds, docstring-only PRs, trivial typos.

## Output

Top 5-10 opportunities:

```
| Repo | Issue | Why fit | Difficulty | Notes |
```

- Repo as `owner/name (<stars>)`
- Issue as clickable link
- Difficulty: easy / medium / hard
- Notes: "good first issue", CLA required, etc.

## Rules

- Never suggest a PR the user already has open on that repo. Cross-reference their open-PR list first (`gh search prs --author @me --state open`).
- Never suggest contributing to a repo that has been inactive >12 months unless the user specifically asks.

$ARGUMENTS
