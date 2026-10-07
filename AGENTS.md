# agent-brain digest

Paste this into any agent that reads rules (Codex, Kiro, Cursor, Zed, Amp). It is
the short form of `rules/always-on.md`; the full skills live in `skills/`.

## Memory first

- Before answering anything the user may have told you before, run
  `brain recall <words>` (or the `recall` MCP tool). The brain folder is
  `$AGENT_BRAIN_DIR`, default `~/.agent-brain`; `INDEX.md` lists every fact.
- Save a durable fact with its source: `brain remember <kebab-name> -d "<one line>" -s "<where it came from>" -b "<fact, why, how to apply>"`.
- A wrong fact is corrected, never edited in place: `brain correct <old> <new> ...`.
  A stale one is withdrawn: `brain forget <name> -r "<reason>"`. History stays on disk.
- Never save secrets. `brain` refuses tokens, keys and JWTs.

## Work

- Do the asked-for thing first; tests, refactors and polish are separate asks.
- A question or a described problem gets an assessment, not a change.
- Public, destructive or config-changing actions need an explicit yes first.
- Search for an existing skill, script or config before creating a new one.

## Proof

- Report only what a tool result in this session shows; mark the rest unverified.
- Green CI is not a working feature. Run it: server up, endpoint hit, UI loaded.
- For a sweep, count the full match set first and report against it ("fixed 12/12").
- A subagent's numbers are claims until you re-measure them.

## Git

- Default branch `main`. Never force-push it, amend pushed commits, or skip hooks.
- Stage files by name. Push new branches with `git push -u origin <b>:<b>`.
- One PR per work stream; follow-ups go to the same branch.
- Never comment on someone else's repo without the user's permission.

## Shell and style

- No `&&` chains: one command per call, or `;` with an explicit `echo "rc=$?"`.
- Never write an em dash or en dash; use `--` or `-`. No emojis in commits or PRs.
- Conventional commits, lowercase, imperative.
