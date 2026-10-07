---
name: no-ampersand-chaining
description: "Never chain shell commands with && in an agent's Windows/MINGW shell -- one command per call, or newline/semicolon separation with explicit exit-code checks"
type: feedback
source: "observed 2026-08-04 when a compile-then-run chain returned a misleading exit code"
created: 2026-08-04
modified: 2026-10-07
status: active
visibility: public
---

Do not use `&&` to chain shell commands. Run one command per Bash call, or separate steps with newlines or `;` inside a single call. Pass absolute paths instead of `cd X && cmd`, or put `cd` on its own line. When a later step must be skipped on failure, check `rc=$?` explicitly rather than relying on `&&`.

**Why:** it misbehaves in a Windows/MINGW agent environment. A compound command can trigger a permission prompt, and a failing chain collapses into one misleading exit code. Concrete case: `g++ -O2 -o e e.cpp 2>&1 | head && ./e` returned 127, which reads as "g++ not found". `g++` was on PATH and the compile succeeded; the real failure was a stack overflow in the program. Splitting the chain into separate lines exposed it immediately, after several minutes spent debugging the wrong thing.

**How to apply:**

```bash
g++ -O2 -o e e.cpp
echo "compile rc=$?"
./e
echo "run rc=$?"
```

- Commands handed to a user on Windows may run in PowerShell 5.1, which has no `&&` at all. Use a single command with a directory flag (`uv run --directory X`, `pnpm --dir X`) or separate steps with `;`.

Related: [[cpp-mingw-debugging-gotchas]] (exit 127 as a stack overflow), [[windows-bash-gotchas]].
