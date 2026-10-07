---
name: stale-snapshot-worklists
description: "A worklist file generated from a one-time snapshot reports DONE when it drains, not when the work is done -- re-derive from live data before each chunk"
type: feedback
source: "observed 2026-08-05 when a resumable voting script reported 0 remaining against a 10-day-old worklist"
created: 2026-08-05
modified: 2026-10-07
status: active
visibility: public
---

Any resumable script driven by a static worklist file will eventually report a confident, completely false "0 remaining". Its completion signal means "my snapshot is drained", never "the work is finished".

**Why:** a resumable script logged "195 done, REMAINING 0" and wrote an `ALL_DONE` marker. A live query across all 299 items showed **272 done, 27 not**. The root cause was structural, not a one-off bug: the todo file had been generated ten days earlier and nothing ever appended to it, so every item created since was invisible to the script. Two pipelines (produce, act) with no channel between them; the second never learns about the first.

**How to apply:**

- Before each chunk of a sweep, re-derive the worklist from the live source of truth, then report progress against a freshly counted total ("276/299"), not against the script's own tally.
- Treat an `ALL_DONE_*` marker file as advisory. Verify with one live query before repeating it to the user as fact.
- When two pipelines mutate the same set, either have the producer append to the consumer's list or make the consumer stateless (derive-then-act every run). A shared static file between them is the bug.
- Generalizes past scripts: the same shape applies to any gap file, backlog, alert list, or TODO list built by an earlier enumeration pass.

Related: [[verify-subagent-numbers-before-publishing]], [[dependency-sweep-gotchas]].
