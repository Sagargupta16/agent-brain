---
name: cpp-mingw-debugging-gotchas
description: "C++ on Windows/MinGW -- exit 127 can be a stack overflow, sub-microsecond timings read as zero, and tail-call asymmetry makes recursion depth direction-dependent"
type: reference
source: "observed 2026-08-05 while measuring algorithm solutions with g++ -O2 on Windows"
created: 2026-08-05
modified: 2026-10-07
status: active
visibility: public
---

- **Exit code 127 with no output can be a stack overflow, not a missing binary.** A program that blows the stack dies with 127, which reads exactly like "g++ not found". Distinguish: confirm the compile returned `rc=0` and the `.exe` exists, then rerun with `setvbuf(stdout, NULL, _IONBF, 0)` plus staged prints to see how far it got. The default stack is 1 MB; build with `-Wl,--stack,268435456` to test deep recursion. A `&&` chain hid this for several minutes of PATH debugging, see [[no-ampersand-chaining]].
- **Sub-microsecond timings read as `0.000 us`** because a single call is below clock resolution. Time a loop of about 200,000 calls and divide, and subtract a measured copy-only baseline (in one case the harness's own input copy was 0.021 us of a 0.080 us figure).
- **Tail-call asymmetry in recursive tree/graph traversal.** At `-O2`, a recursive call in tail position becomes a jump and costs no stack; the same call NOT in tail position consumes a real frame. In-order DFS was therefore safe on a 100,000-node right chain (`iter(r->right)` is last) and stack-overflowed on a 20,000-node left chain (`iter(r->left)` has work after it). Never conclude "recursion depth is fine" from testing one direction. With n up to 1e5 and no balance guarantee, use an explicit stack.

**Why:** each of these produced a confident wrong conclusion before it was written down; the timing one hit twice.

Related: [[verify-subagent-numbers-before-publishing]], [[no-ampersand-chaining]].
