---
name: verify-subagent-numbers-before-publishing
description: "A drafting subagent's measured-sounding numbers are not measurements -- re-measure every factual claim before it publishes under your name"
type: feedback
source: "observed 2026-08-03 auditing five agent-drafted algorithm solution articles"
created: 2026-08-03
modified: 2026-10-07
status: active
visibility: public
---

When a subagent produces content that will go out publicly under your name, re-derive every number and every factual claim locally before it ships. Confident, specific, measured-sounding figures from an agent are frequently invented.

**Why:** an audit of five agent-drafted articles, each asserting a defect in an accepted solution, found two wrong statistics and one claim that was the OPPOSITE of reality:

- `maximum-gap`: claimed 106,406/200,000 fuzz failures. Real figure 84,286 (42.1%), stable across seeds.
- `maximal-square`: claimed 282/300 grids wrong. Real figure 233/300, and only under a condition the agent had not stated (it needs a large SOLID block, not merely a large grid).
- `min-stack`: both timings understated (10.2 ms measured vs 4.52 claimed; 82.8 vs 36.7) and the comparison count was off by 2x.
- `binary-search-tree-iterator`: the article said a 100,000-node all-left chain "completed in 1.2 ms ... small enough to survive". It **stack-overflows**, and so does 20,000 nodes on a 1 MB stack. A false safety claim is worse than a missing one.

The defects themselves were all real. It was the supporting evidence that was fabricated, which is the harder failure to spot, because a true conclusion makes you stop checking.

**How to apply:**

- Compile and run it. For C++, `g++ -O2 -std=c++20` in a scratch directory, measure at the constraint ceiling, and state overflow bounds explicitly.
- Cross-check against an **independent formulation**, not a rewrite of the same idea. Two unrelated mechanisms agreeing is what rules out a bug in the reference itself (for example fixpoint relaxation vs Floyd-Warshall closure; sort-then-walk-gaps vs `std::set` difference).
- Prefer exhaustive over random testing where the domain allows it, and report the outcome MIX so both branches are provably exercised ("5,920 blocked / 10,464 removed"), not just "0 mismatches".
- If a claim does not reproduce, correct every occurrence of the figure, not just the first. Wrong numbers get restated in the summary, the body, and the verification section.

Generalizes the rule "a workflow or subagent summary is not the diff". Related: [[stale-snapshot-worklists]], [[multi-agent-fanout-workflow]], [[cpp-mingw-debugging-gotchas]].
