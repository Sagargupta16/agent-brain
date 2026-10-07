# agent-brain

My agent setup, packaged so you can use it and so our agents can learn from each
other: 15 skills, 7 subagents, safety hooks, always-on rules, and a **brain**, a
markdown memory that Claude Code, Codex and Kiro all read and write.

It encodes one opinionated workflow (DevOps and full-stack work across 60+ repos
on GitHub, mostly on Windows with Git Bash). Take the parts that fit, skip the rest.

## What's inside

| Part | What it is | Where |
| --- | --- | --- |
| Brain | One fact per markdown file, with its source. Facts get corrected or withdrawn, never silently overwritten. Keyword recall (BM25), an `INDEX.md`, and a stdio MCP server. Python standard library only | [`bin/brain.py`](bin/brain.py) |
| Learnings | 27 public lessons from real failures (lockfile drift, PR checks that stall, SonarCloud gates, Windows shell traps), each failure paired with the fix that worked | [`brain/learnings/`](brain/learnings/README.md) |
| Playbooks | Debugging, review bar, git workflow, refactor rules, session patterns, stack decisions | [`brain/playbooks/`](brain/playbooks/README.md) |
| Skills | `save-session`, `memory-router`, `ship`, `prod-check`, `fix-all`, `sonar-sweep`, `gh-actions`, `repo-audit`, `harness-audit`, `parallel`, `ideate`, `docs-fresh`, `aws-ops`, `db-ops`, `oss` | [`skills/`](skills/) |
| Subagents | code-reviewer, debugger, dependency-updater, git-assistant, pr-analyzer, refactorer, test-runner | [`agents/`](agents/) |
| Hooks | Block destructive shell commands, `--no-verify` and force-push to main; block new em/en dashes; remind to save before compaction | [`hooks/`](hooks/) |
| Rules | Always-on rules (git safety, secrets, proof before "done", delivery order), plus Python, JS and IaC rules and an example prompt vocabulary | [`rules/`](rules/) |
| Digest | The rules in about 2 KB, for any agent that reads `AGENTS.md` | [`AGENTS.md`](AGENTS.md) |

## Install

Claude Code plugin (skills, subagents and hooks):

```
/plugin marketplace add Sagargupta16/agent-brain
/plugin install agent-brain@agent-brain
```

Everything, for one or more hosts (rules, digest, brain folder, MCP registration):

```bash
git clone https://github.com/Sagargupta16/agent-brain ~/agent-brain
```

```bash
~/agent-brain/install.sh --host all --seed --dry-run
```

Drop `--dry-run` once the plan looks right. `--host` takes `claude`, `codex`, `kiro`
or `all`; `--seed` copies the public learnings into your brain. The installer never
overwrites a file it did not write unless you pass `--force`.

## The brain

```bash
brain remember npm-matches-node -d "Match npm major to the CI Node version" -s "lockfile failed npm ci on 2026-10-06" -b "Node 22 ships npm 10; write the lockfile with npx -y npm@10."
brain recall lockfile npm ci
brain correct npm-matches-node npm-major-per-node -d "..." -b "..." -s "re-checked"
brain forget npm-major-per-node -r "CI moved to Node 24"
brain lint
brain export ./share   # copies only pages marked --public
```

The folder is `--dir`, else `$AGENT_BRAIN_DIR`, else `~/.agent-brain`. Point it at
an existing Claude Code memory folder and `recall` works on it as is.

- **Sources.** Every page has a `source`, so an agent can say where a fact came from.
- **Corrections keep history.** `correct` writes a new page and marks the old one
  `corrected` with a pointer. `forget` marks a page `withdrawn` with a reason. Neither
  is recalled again, and neither is deleted.
- **Private by default.** Pages are `visibility: private` unless saved with
  `--public`, and `brain` refuses text that looks like a token, key or JWT.
- **Every agent, one memory.** `brain mcp` serves `recall`, `remember`, `correct` and
  `forget` over stdio, so any MCP client sees the same facts.

## Share what your agents learned

1. Save lessons with `--public` when they hold no private detail.
2. `brain export ./share`, then open a PR adding the pages to `brain/learnings/`.
3. `python scripts/check.py` must pass: no dashes, no secrets, no home paths,
   valid frontmatter, no broken links. Set `AGENT_BRAIN_LEAKWORDS` to a local file of
   private words (project names, employer) to block those too.

## Checks

```bash
python scripts/check.py
```

```bash
python scripts/test_hooks.py
```

Both run in CI with `skillcheck` on every push.

## Credits

Ideas, not code, from three projects worth reading:

- [garrytan/gbrain](https://github.com/garrytan/gbrain): memory with provenance,
  correction and withdrawal, one brain for every agent over MCP, start keyless.
- [garrytan/gstack](https://github.com/garrytan/gstack): one installer across agent
  hosts, and a short rules digest for any agent that reads `AGENTS.md`.
- [pbakaus/impeccable](https://github.com/pbakaus/impeccable): deterministic checks
  that run with no LLM, as the gate in front of the judgment calls.

## License

MIT
