# Contributing to agent-brain

agent-brain is an agent harness (skills, subagents, hooks, rules) plus a markdown brain that Claude Code, Codex and Kiro share. Bug reports, fixes, doc corrections and new public learnings for `brain/learnings/` are welcome.

## Setup

There is nothing to install. The brain and the checks are Python standard library only (Python 3.10 or newer; CI uses 3.13), and the installer and hooks are POSIX shell.

```bash
git clone https://github.com/Sagargupta16/agent-brain
cd agent-brain
d=$(mktemp -d)
python bin/brain.py --dir "$d" recall <words>
./install.sh --host all --seed --dry-run
```

Leave off `--register-mcp` while you test the installer: it runs `claude mcp add` and `codex mcp add` against your real config. On Windows a fake `HOME` does not isolate that.

## Before you open a PR

CI (`.github/workflows/ci.yml`) runs these on every push to `main` and every pull request. Run them from the repo root:

```bash
python scripts/check.py
python scripts/test_hooks.py
npx -y @sagargupta1610/skillcheck@0.2.5 lint skills
python -c "import json; json.load(open('.claude-plugin/plugin.json')); json.load(open('.claude-plugin/marketplace.json')); json.load(open('hooks/hooks.json'))"
```

CI also runs a brain round trip:

```bash
d=$(mktemp -d)
python bin/brain.py --dir "$d" remember ci-fact -d "CI round trip" -s "ci" -b "hello brain"
python bin/brain.py --dir "$d" recall hello | grep -q ci-fact
python bin/brain.py --dir "$d" forget ci-fact -r "done"
python bin/brain.py --dir "$d" lint
```

- `scripts/check.py` must report 0 problems. It blocks en and em dashes (write `--` or `-`), secret-shaped strings, absolute home paths, bad skill frontmatter, broken relative markdown links and brain page problems.
- `scripts/test_hooks.py` needs bash and jq. On Windows it uses Git Bash; set `HOOK_BASH` to use another bash.
- skillcheck runs through `npx`, so you need Node.
- Optional: point `AGENT_BRAIN_LEAKWORDS` at a local file of private words, one per line, and `check.py` blocks those too. Never commit that file.

## Conventions

- Everything in this repo is public. Do not add personal names, home paths, private project names, employer details, account IDs or PR numbers from private history.
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`), lowercase and imperative.
- Skills: `name` in the frontmatter equals the folder name, and `description` is a `>-` folded block with no unquoted `: `.
- Learnings: one lesson per file in `brain/learnings/`, the failure paired with the fix that worked, `visibility: public`, using the frontmatter fields listed in [brain/learnings/README.md](brain/learnings/README.md). Add a row for it to that table. Cross-links use `[[<slug>]]`.
- To share lessons from your own brain: save them with `--public`, run `brain export ./share`, then open a PR that adds the pages to `brain/learnings/`.
- If you add or remove a skill or subagent, update the counts in `README.md` and `.claude-plugin/plugin.json`.
- The installer never overwrites a file it did not write unless `--force` is passed, and never edits a harness JSON config itself. Keep both properties.
- Line endings are LF (`.gitattributes`), except `*.cmd` files, which stay CRLF.

## Security issues

Do not report vulnerabilities in public issues. Follow [SECURITY.md](SECURITY.md).

## License

agent-brain is released under the MIT License (see [LICENSE](LICENSE)). By contributing, you agree that your contributions are licensed under it.
