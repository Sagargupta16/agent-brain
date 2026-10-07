---
name: debugging-playbook
description: "Reproduce, isolate, fix, regression-test loop, plus common error patterns, debug tools by stack, and how to report a fix"
type: playbook
source: "ported from a private multi-repo workspace playbook"
created: 2026-10-07
modified: 2026-10-07
status: active
visibility: public
---

# Debugging Playbook

## The loop

**Reproduce -> Isolate -> Fix -> Regression test.** Skip a step, pay for it later.

1. **Reproduce** -- get a deterministic repro. Minimal input, minimal setup.
2. **Isolate** -- bisect. Binary search the code, the commits, the inputs.
3. **Fix** -- smallest change that makes the repro pass.
4. **Regression test** -- write the test that would have caught this, before the fix lands.

## When the user pastes a terminal transcript

- Parse the error line directly.
- Propose a one-line fix if obvious.
- Do not ask them to reformat or re-paste.
- Do not narrate what the error means at length -- fix first, explain if asked.

## Common error patterns

### Auth loops (Bedrock / OpenAI-compatible gateways)

- Confirm the auth method FIRST: bearer vs SigV4 vs OAuth. See the learning `verify-integration-auth-first`.
- Check `CLAUDE_CODE_USE_BEDROCK`, `AWS_REGION`, `ANTHROPIC_BEDROCK_BASE_URL`.
- 401/403 -> token or credentials. 404 on a model id -> wrong region or model slug.

### CRLF noise in git (Windows)

- Inflated dirty counts are line-ending flips, not real edits. Do not commit the flip -- `git checkout -- <file>` if the diff is pure CRLF.

### Renovate / CI failures

- Check the `renovate.json` schema first (most failures are config drift).
- Match the org's Renovate preset. Do not reinvent.

### API + SPA dev loop

- CORS misconfig: 401 on OPTIONS, 200 on GET -> preflight.
- Port conflicts: check which process holds the backend port and the frontend dev port (Vite 5173, Next 3000) before changing config.

## Debug tools by stack

### Python

- `breakpoint()` (not `pdb.set_trace()`).
- `rich.traceback` for prettier stacks.
- `logging.DEBUG` at module level, not `print`.
- `pytest --pdb` drops into the debugger on failure.

### JS/TS

- `debugger;` + browser DevTools.
- `console.log` for quick checks, **remove before commit**.
- React DevTools for component state.
- Network tab before blaming the backend.

### Git

- `git bisect` when a bug appeared between two known states.
- `git log -S "string"` to find when a literal was added or removed.
- `git reflog` before `git reset --hard` anything.

## When stuck

- **Read the actual error, not the first line.** Stack trace bottom-up.
- **Revert the last change** -- does the bug persist? If no, you are close.
- **Rubber-duck in the reply.** State assumptions; the user will often spot the wrong one.
- **Do not thrash.** After 3 failed attempts at the same angle, change angle. For calculations, stop after 2 and list the formulas.
- **Subagent for research** when the bug is in unfamiliar territory -- keeps main context clean.

## When reporting back

- **What broke** -- one line.
- **Root cause** -- one paragraph.
- **Fix** -- diff or command.
- **Regression test** -- where it lives.
- **Sibling updates** -- did this affect docs, CHANGELOG or status tracking?
