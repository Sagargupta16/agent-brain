# CLAUDE.md - agent-brain

> This file stacks on top of the workspace root at `C:\Code\GitHub\`:
> - Root [`CLAUDE.md`](../../CLAUDE.md) -- voice, rules, routing map, references, skills, slash commands, conventions.
> - Root [`MEMORY.md`](../../MEMORY.md) -- live facts across repos.
> - Root [`STATUS.md`](../../STATUS.md) -- live PR/CI/security dashboard.
> - [`.claude/resources/`](../../.claude/resources/README.md) -- deep reference for collaboration, workflow, git, OSS, debugging, voice.
>
> Read those first. The guidance below only adds **repo-specific context** -- it does not override anything in the root.

## Project

Public, sanitized export of the personal agent harness (skills, subagents, hooks, rules) plus a shared markdown brain (`bin/brain.py`, stdlib Python) that Claude Code, Codex and Kiro read over CLI or stdio MCP. Ideas credited to gbrain, gstack and impeccable; no code copied from them.

## Stack

- **Language**: Python 3.10+ standard library (brain, checks), POSIX shell (installer, hooks)
- **Package manager**: none; no runtime dependencies
- **Deploy target**: GitHub repo + Claude Code plugin marketplace (`.claude-plugin/`)

## Run

```
python bin/brain.py --dir /tmp/b recall <words>
python scripts/check.py
python scripts/test_hooks.py
./install.sh --host all --seed --dry-run
```

## Rules for this repo

- **Everything here is public.** The source of truth for skills, rules and hooks is `~/.claude/`; this repo holds sanitized copies. Port changes by hand and re-sanitize: no personal names, home paths, private project names, employer details, account IDs or PR numbers from private history.
- `python scripts/check.py` must report 0 problems before any commit. Run it with `AGENT_BRAIN_LEAKWORDS` pointing at a local, never-committed word list of private names.
- Skill frontmatter: `name` equals the folder, `description` is a `>-` folded block with no unquoted `: `. Lint with skillcheck.
- Learnings in `brain/learnings/` are one lesson per file, failure paired with the fix, `visibility: public`. `brain lint` must pass.
- The installer never overwrites files it did not write without `--force`, and never edits a harness JSON config itself; it prints the MCP line instead.
