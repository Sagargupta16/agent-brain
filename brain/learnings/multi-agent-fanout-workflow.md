---
name: multi-agent-fanout-workflow
description: "Run multi-file audits as parallel scouts, one synthesizer, per-file fixers and parallel verifiers; review the diff yourself because the workflow summary describes intent, not reality"
type: feedback
source: "observed 2026-07-04 on a 28-finding chart audit, extended 2026-09-30 with a 9-lane parallel cleanup pass"
created: 2026-07-04
modified: 2026-10-07
status: active
visibility: public
---

Substantive multi-file audits run better as an orchestrated fan-out than as solo edits. The pattern that worked:

1. **Discover:** about 5 parallel scout agents, each scoped to one dimension (single-file pages, multi-file pages, chart primitives, hooks, backend endpoints), all returning one shared JSON schema (`file, target, problem_present, fix_needed, reason, suggested_fix`).
2. **Synthesize:** ONE agent takes all findings, the user's verbatim request, and the strategy options (shared util vs hook-level vs backend) and emits a concrete edit plan (a `shared_util` block and a `per_file_edits` array). Run it at high effort; plan quality gates everything downstream.
3. **Shared:** one agent creates the shared util plus its tests, if the plan calls for it.
4. **Per-file:** one fixer per file, in parallel, with hard "surgical only" rules (no formatting, no cleanup, no commits).
5. **Verify:** three parallel agents run type-check, lint and tests, each returning `PASS` or `FAIL:<snippet>`.

**Why:** the audit turned 28 findings into 2 planned edits (one shared util at the root plus one site-level bug) with 17 files intentionally skipped. Solo would have taken 20+ read/edit cycles and burned main-loop context on the survey. The fan-out kept the main loop clean and let the synthesizer see all perspectives at once.

**How to apply:**

- Use orchestration only when the user asked for it ("fan out", "use a workflow", "parallel agents") or the harness mode has it switched on.
- Always paste the user's verbatim request into the synthesizer prompt so it cannot drift.
- Make the synthesizer list `intentionally_skipped` explicitly; it forces out-of-scope decisions to be visible.
- After the workflow returns, ALWAYS review the diff yourself before committing.
- Long agents can stall at a stream watchdog (about 600 s) on a single long tool call such as a full test suite or a big build. Their transcript and working-tree edits survive; messaging the agent by id resumes it. Tell agents to keep each tool call short, run full suites in the background and poll.
- An agent can finish without delivering its report; message it to hand the report back.
- Lanes sharing one working tree need disjoint file ownership, plus a final sequential integration pass for cross-lane leftovers.

Related: [[verify-subagent-numbers-before-publishing]], [[subagent-denials-cannot-be-retried]], [[agent-execution-patterns]].
