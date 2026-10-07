---
name: dependency-sweep-gotchas
description: "Reusable fixes from a multi-repo Dependabot sweep -- npm version matching, Renovate lockfile gaps, yarn 1, pnpm floors, unpatchable advisories"
type: reference
source: "observed 2026-10-06 during a 21-repo Dependabot sweep (159 -> 18 alerts, 26 fix PRs, 5 parallel lanes plus a rescan pass)"
created: 2026-10-06
modified: 2026-10-07
status: active
visibility: public
---

Each item is a failure paired with the fix that worked.

- **Match npm to CI's Node.** Node 22 CI ships npm 10 (`npx -y npm@10`), Node 24+ ships npm 11. A lockfile written by the wrong npm fails `npm ci` ("Missing: yaml@2.9.1 from lock file") or churns `libc` fields. Verify with `npx -y npm@<n> ci --dry-run` before pushing.
- **Never use `npm --prefix <dir>` for lockfile work.** npm 10 injected a bogus `"server": "file:.."` dependency. `cd` into the package directory instead.
- **Renovate in uv repos can bump only `requirements.txt`.** It skips `uv.lock`. Run `uv lock --upgrade-package <pkg>`, then re-export with the repo's own `uv export` command; CI diffs the two. uv may hold a pin the export moved (for example `pydantic-core` stays tied to `pydantic`).
- **Two lockfile PRs collide.** After merging one, rebase the other, take main's lockfile with `git checkout --ours <lockfile>`, regenerate, then `git rebase --continue`. Renovate auto-merge can land a PR while you work on a sibling.
- **Classic yarn 1 will not move an in-range transitive.** Delete its lockfile entries and reinstall, or add a scoped `resolutions` entry.
- **pnpm `update` may not move a transitive** (seen with `source-map-js` on pnpm 11.17). Add a commented floor under `overrides:` in `pnpm-workspace.yaml` (for example `'>=1.2.2 <2'`) and run `pnpm install --lockfile-only`.
- **Dependabot rescans at merge time and raises new alerts** for manifests the first pass skipped (sibling lockfiles, a `site/` folder, a nested test app). Always recount alerts live after merging and run a second pass. See [[stale-snapshot-worklists]].
- **Some advisories have no patched release** (braces GHSA-vfj7-8cjw-p6xm, sprintf-js, node-forge as of 2026-10-06). Dev-only audit gates stay red; the fix that held was moving those repos to a prod-only audit (`pnpm audit --prod`, `npm audit --omit=dev`).
- **Create React App lock-in.** webpack-dev-server 5 and svgo 2 break react-scripts 5 (`onAfterSetupMiddleware` unknown, `new SVGO()` removed). Those alerts only clear by moving off CRA.

**How to apply:** enumerate the live alert count per repo first, fix in lanes, recount live after every merge, and report "fixed N/M" against the fresh count.

Related: [[python-tooling-gotchas]], [[stale-snapshot-worklists]].
