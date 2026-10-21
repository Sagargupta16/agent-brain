# Changelog

## 0.1.2 (2026-10-21)

### Added

- An architecture diagram at the top of the README: Claude Code, Codex and Kiro share one brain through `brain mcp` over stdio, the Claude Code plugin's hooks, skills and subagents, and the path a public lesson takes into `brain/learnings/` and back out with `install.sh --seed`.
- A state diagram of a fact page (active, corrected, withdrawn, never deleted) in the brain section of the README.
- Both are orrery specs in `docs/diagrams/` (`architecture.yaml`, `fact-lifecycle.yaml`), rendered to light and dark SVGs. Their `evidence:` entries point at the file and line each part comes from, so `orrery verify` can check them.

## 0.1.1 (2026-10-18)

### Fixed

- `hooks/block-dangerous.sh` let a force-push to main through when the flag came after the branch (`git push origin main --force`), and missed `--force-with-lease`, `+main` and `HEAD:main` refspecs. The hook now splits the command into words, so flag order and refspec form no longer matter. It also blocks deleting main on the remote and a force-push that names no branch.
- The same hook no longer blocks a commit whose message only mentions `--no-verify`; quoted text is ignored when checking flags.

### Added

- `hooks/block-dangerous.sh` blocks `git commit -n`, `rm` on a drive root or the home directory however it is spelled, and reading secret files (`.env`, SSH keys, `.netrc`, cloud credentials) through the shell. `.env.example` and public keys stay readable.
- `scripts/test_hooks.py` covers 46 shell commands, blocked and allowed.

## 0.1.0 (2026-10-07)

- First release: brain, learnings, playbooks, 15 skills, 7 subagents, hooks and rules.
