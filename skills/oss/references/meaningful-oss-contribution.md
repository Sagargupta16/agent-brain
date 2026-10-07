---
name: meaningful-oss-contribution
description: >-
  How to make an open-source contribution that actually MERGES and MATTERS --
  the method, quality bar, PR anatomy, and etiquette, grounded in analysis of
  real merged and rejected PRs and maintainer wisdom. Use when the user wants
  to contribute to a repo, evaluate whether a candidate issue or PR is worth
  doing, shape a PR for merge, or decide go/no-go on an upstream
  contribution. Pairs with find-contributions (sourcing) and upstream-pr-prep
  (pre-flight).
---

# Meaningful OSS Contribution

Distilled from empirical analysis of real merged + rejected PRs (axios, pandas, TypeScript, vite, httpx, prometheus, rust, react, zulip, k8s) and maintainer writing (opensource.guide, Tsay/Dabbish/Herbsleb ICSE 2014, Dey & Mockus ESEM 2020, curl's Daniel Stenberg, Hanselman, Kubernetes/rust AI policies). Pairs with the `find` mode reference for sourcing and the `prep` mode reference for the fork/upstream workflow.

## What "meaningful" means

A contribution is meaningful when it solves a problem **the project actually has**, not one you invented to generate activity.

**The inversion test:** if the only beneficiary is you -- a resume line, green squares, a merged-commit badge, a bounty -- it is vanity. If a bug you personally hit, a documented high-reaction issue, or a code path many users share gets fixed, it is meaningful.

**Impact scales with blast radius, not diff size.** A one-character fix in axios `isAbsoluteURL()` (deleting a `?`) closed an SSRF affecting every axios user. A one-line change fixed a 10x httpd slowdown. **Small diff + deep understanding + broad blast radius = the ideal.** Cosmetic README/whitespace edits, drive-by lint runs, and AI "optimizations" that mute errors instead of fixing root cause are the canonical non-meaningful patterns maintainers auto-reject.

## The 7+/10 quality bar -- score before investing

Only proceed if a candidate clears ~7. Failing **provenance, root-cause, or can-explain-it** is drive-by noise no matter how clean the diff:

1. **Provenance** -- did I personally hit this, or is it a real open issue? Invented value scores 0.
2. **Blast radius** -- shared code path (security/perf/data-loss/hot-path) vs a +2-reaction edge case?
3. **Root cause** -- can I name WHY it broke (git-blame the introducing commit, the violated invariant), not just the symptom?
4. **Legibility** -- one logical change, ideally 1-3 files, approvable without the reviewer re-deriving it?
5. **Provability** -- a reproduction + a regression test that FAILS on old code, PASSES on new?
6. **Alignment** -- within the project's stated scope/roadmap, or a useful-but-unaligned maintenance liability?
7. **Ownership** -- can I be "paged" for this code, explain every line in my own words, and stay through review?

## The method (in order)

1. **Source from what you use.** Bugs/friction in software you run daily hand you a free reproduction, version info, and the motivation to survive review. Do NOT race `good first issue` on 50k-star repos -- that pool is diluted, the genuinely-easy issues there are usually *unlabeled*, competing PRs often exist, and you arrive with zero prior interaction (the weakest acceptance position).
2. **Verify the repo is open-shop.** `gh pr list --repo O/R --state merged --limit 20 --json author` then check `author_association` on recent merges. All MEMBER/COLLABORATOR = effectively core-team-only (stalls outsiders). Presence of CONTRIBUTOR / FIRST_TIME_CONTRIBUTOR = genuinely open. A "contributions welcome" README means nothing; merge cadence from non-core authors is the real signal. Prefer 1-2 maintainers + a backlog of simple unlabeled issues.
3. **Read CONTRIBUTING.md, README, and recent merged PRs first.** Dictates commit convention, target branch (docs often go to `stable`), test requirements, PR template, triage-bot behavior. Skipping it starts you with negative goodwill -- maintainers instantly read "didn't read the docs."
4. **Build prior-interaction capital before your first code PR.** (Tsay et al: prior interaction raises acceptance AND buffers the negative effect of heavy discussion.) Confirm a repro, add a minimal reproducible example to a vague bug, answer a tracker question. Triage is the highest-leverage no-code entry point -- maintainers spend ~10-20 min/issue and want the help.
5. **Claim correctly, per the repo's model.** Three exist: HARD label-gate (cli/cli bot rejects PRs with no linked `help wanted` issue), HARD claim-lock (zulip's bot refuses a 2nd claimant, closes cold duplicates), SOFT self-assign (`@rustbot claim`). Features -> comment your approach, get maintainer ack/label BEFORE coding. Small already-labeled bugs -> clean cold-PR with `Fixes #NNN` is fine and fastest. Docs/typos -> lightest touch.
6. **Fix the root cause once, where all callers route through.** grep every caller before editing; put the guard in the single shared function so sibling paths are fixed too -- smaller diff than patching each caller. But don't over-expand: fix the shared root cause in one place, not every call site. A dependency bug -> upstream it; a local monkeypatch unblocks only you and is not a contribution.
7. **Write the regression test first** so it fails on current code, then make it pass. Name it after the issue/CVE with an inline `# GH NNNNN`. For docs/typos, strike the tests checkbox with a one-line reason. "Works locally" is not evidence maintainers accept.
8. **One clean commit, green CI, then request review.** Draft while fixing checks; mark ready only when green. Clear ALL automated gates first (CLA/EasyCLA, release-note block, linter, triage/approval labels) -- these block you before a human looks. Strangers get no benefit of the doubt on red CI.
9. **Respond to every review comment, fast, in your own words,** with an itemized "done, done, done" checklist. Bake resolved discussions back into the code, not just the thread. Silence is the #1 killer of newcomer PRs.
10. **Budget days-to-weeks for response** (median first ack: rust ~8.5h, cli/cli ~23h, home-assistant ~30h; rust documents a 2-week reviewer SLA). Wait ~a week, then ONE polite in-thread nudge. Never DM/email to chase a review.

## PR anatomy (the body does the reviewer's job)

Structure the PR body so approval is a rubber-stamp -- the reviewer never re-derives anything:

```
## Problem      -- what's broken, for whom (link the issue: Fixes #NNN)
## Root cause   -- file:line or a code snippet; WHY it breaks
## Fix          -- show the change; cite symmetric prior art / the introducing commit SHA
## Test / safety -- the regression test; a runnable before/after (repro, profiler trace, snapshot)
```

- **Link the issue** with a closing keyword (`Fixes #NNN`) -- auto-links, auto-closes, satisfies triage bots. Behavior changes need a linked issue or prior discussion; docs/typos are the sanctioned exception.
- **Cite prior art** to kill doubt: "This is the symmetric case of #NNN; the fix mirrors it" or the exact commit SHA that motivates the change -> merges near-instantly.
- **Make before/after runnable, not described:** paste the repro, a profiler flame trace, a whatsnew Previous/New block, a failing snapshot. Evidence, not adjectives.
- **Match house style exactly:** fill the PR template verbatim, use their commit convention, target the branch they specify, match surrounding code.
- **Keep it small and single-purpose** (1-3 files). Review quality collapses past ~200-400 lines; more files-changed more than doubles time-to-merge. No drive-by refactors or "while I'm here."
- **State honestly what it does and doesn't do.** Precise scoping ("reduces compounding effects, doesn't fully fix") builds trust; overclaiming erodes it. A regression test alone can be a welcomed contribution.

## Green flags

- You hit the bug in software you use; you have a repro + version/env.
- You can name the root cause and cite the introducing commit.
- Tiny diff, deep understanding, fix in the one shared function.
- Same-PR regression test that's red-before/green-after.
- Body reads Problem -> Root cause -> Fix -> Test, links `Fixes #NNN`, cites prior art.
- Prior-interaction capital built first; claimed correctly; matched template/convention/branch; green CI; all gates cleared.
- You respond fast and stay engaged; you picked an open-shop repo.

## Red flags (each burns reputation)

- **Bot-cadence prose:** "All issues fixed! Checks passing! Ready whenever you get a chance! Thanks!", a multi-paragraph essay for a trivial diff. This alone got a bors-approved rust PR closed and a clean k8s fix rejected on AI policy. Correct code does not survive AI-slop presentation.
- **Duplicate of an in-flight PR** -- not checking existing OPEN PRs + issue backlinks is the #1 wasted-effort pattern ("teach your LLM to look at the existing backlinks").
- **Cold-PRing a claimed/in-progress issue** -- closed same day against an active claim.
- **Large/mixed-purpose PR** (refactor + bug + feature + deps) -- closed unreviewed as "too much to review." If the description needs bullet points, it's too big.
- **Behavior change with no test**, or "trust me it works locally."
- **Empty/generic body** ("fixed a bug") that forces reverse-engineering.
- **AI "fixes" that mute an error** instead of fixing root cause; hallucinated function names/addresses in security reports (the curl AI-slop signature that killed its bug bounty).
- **Contributing for the reward** (t-shirt, squares, bounty, resume) as the primary goal; cosmetic PRs "just to have a PR."
- **Batching trivial typo fixes across many repos** -- indistinguishable from spam even when each is correct.
- **Test/learning/"Just checking" PRs against flagship repos** -- use your own fork.
- **Arguing past a "decline to merge"** or re-pushing "ready for review" after the maintainer says the direction is wrong. Repeat low-effort AI contributions escalate from PR-closed to author-BANNED.

## Worked examples (the shape of a merge)

- **axios#6539 (SSRF):** deleted ONE `?` from a regex; +49/-4 (mostly test); links the CVE, ships a regression test standing up good+bad servers. Tiny diff, huge blast radius, runnable proof.
- **vite#22781 (genuine outsider):** +7/-1, one guard on an unguarded `decodeURIComponent`; body cites "symmetric case of #22714, fix mirrors it" -> 0 comments, member-approved same day. The gold standard external merge.
- **httpx#3579 (first PR ever to the repo):** re-adds mistakenly-deleted docs, cites "taken from commit 3f7657, the last before it was removed," strikes the tests checkbox with a reason, flags unrelated build warnings with pasted output. Textbook first-timer docs on-ramp.
- **pandas#45084:** overflow forced a hard ValueError blocking legit large frames; fix downgrades to PerformanceWarning in the ONE `_Unstacker` both callers route through; adds whatsnew Previous/New blocks + `# GH 26314` test. Root-cause-in-shared-function.
- **TypeScript#30775 (tsc 20x slower):** uncached substitution types defeated the conditional-type cache; +8/-1 adds a cache map; the `.types` baseline snapshot IS the test. Framed honestly: "doesn't fully fix anything per se, but reduces compounding effects."
- **Counter-examples:** rust#158509 -- valid, bors-r+'d fix closed *solely* for LLM-written description. react#36866/#36850/#36856 -- three duplicate PRs closed for not checking backlinks. A Burn-framework PR closed for muting an error instead of fixing root cause, motivated by "a commit on their record."

## Standing rules for the agent

- **7+/10 only; never a duplicate/spam PR.** This reference's quality bar operationalizes that.
- **Never comment on upstream PRs without the user's explicit permission.** Recon, rebase own forks, and draft comment text for approval -- don't post.
- Strong-fit domains are the user's own (`brain recall oss skills`); score Ownership low outside them.
- Highest-yield path: **self-sourced bugs in libraries the user's own repos already depend on** -- the repro comes for free and the fix can be defended in review.
