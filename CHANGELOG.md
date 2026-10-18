# Changelog

## 0.1.1 (2026-10-18)

### Fixed

- `hooks/block-dangerous.sh` let a force-push to main through when the flag came after the branch (`git push origin main --force`), and missed `--force-with-lease`, `+main` and `HEAD:main` refspecs. The hook now splits the command into words, so flag order and refspec form no longer matter. It also blocks deleting main on the remote and a force-push that names no branch.
- The same hook no longer blocks a commit whose message only mentions `--no-verify`; quoted text is ignored when checking flags.

### Added

- `hooks/block-dangerous.sh` blocks `git commit -n`, `rm` on a drive root or the home directory however it is spelled, and reading secret files (`.env`, SSH keys, `.netrc`, cloud credentials) through the shell. `.env.example` and public keys stay readable.
- `scripts/test_hooks.py` covers 46 shell commands, blocked and allowed.

## 0.1.0 (2026-10-07)

- First release: brain, learnings, playbooks, 15 skills, 7 subagents, hooks and rules.
