# Learnings

One lesson per file, each a failure paired with the fix that worked. Frontmatter fields: `name`, `description`, `type` (`reference` for technical gotchas, `feedback` for working-style lessons), `source`, `created`, `modified`, `status`, `visibility`. Cross-links use `[[<slug>]]`.

| Slug | Description |
| --- | --- |
| [agent-execution-patterns](agent-execution-patterns.md) | Execute when asked to do, ask once on ambiguous names, stop after two failed attempts, one PR per stream, never remove what was not asked |
| [agent-harness-gotchas](agent-harness-gotchas.md) | Heredoc parse failures kill the whole command, settings self-edits blocked in auto mode, content hooks fire on checker code, stale diagnostics |
| [airflow-test-patterns](airflow-test-patterns.md) | Apache Airflow test fixtures, the serialization trap, `db_test` marker, PR requirements |
| [bedrock-us-vs-global-profile-latency](bedrock-us-vs-global-profile-latency.md) | Measured `us.` vs `global.` Bedrock profile latency; no meaningful difference |
| [cap-historical-charts-at-today](cap-historical-charts-at-today.md) | Historical charts must not emit data rows past today; cap at the shared hook or per series |
| [claude-desktop-bedrock-config-gotchas](claude-desktop-bedrock-config-gotchas.md) | Where Desktop profile config lives, Setup overwrites edits, picker errors, gateway that drops retention settings |
| [claude-desktop-vm-service-not-running](claude-desktop-vm-service-not-running.md) | "VM service not running" means `CoworkVMService` is stopped; start it, reinstall never helps |
| [cpp-mingw-debugging-gotchas](cpp-mingw-debugging-gotchas.md) | Exit 127 can be a stack overflow, sub-microsecond timings read as zero, tail-call asymmetry |
| [dependency-sweep-gotchas](dependency-sweep-gotchas.md) | npm version matching, Renovate lockfile gaps, yarn 1, pnpm floors, unpatchable advisories |
| [git-on-windows-gotchas](git-on-windows-gotchas.md) | CRLF noise, rebase blocked by unwritable files, gofmt on CRLF, fork detachment |
| [github-marketplace-action-publishing](github-marketplace-action-publishing.md) | Marketplace listing is UI-only, edit an existing tag's release, moving the major tag is normal |
| [github-pr-checks-stall-causes](github-pr-checks-stall-causes.md) | First-time fork runs parked at `action_required`, re-runs replaying a stale merge ref, silent missing labels |
| [github-token-automation-gotchas](github-token-automation-gotchas.md) | `GITHUB_TOKEN` PRs start no runs and skip closing keywords; labeled forms double-fire |
| [money-cells-in-flex-rows](money-cells-in-flex-rows.md) | Amount cells need `shrink-0 text-right tabular-nums whitespace-nowrap` plus a fixed width |
| [multi-agent-fanout-workflow](multi-agent-fanout-workflow.md) | Parallel scouts, one synthesizer, per-file fixers, parallel verify; review the diff yourself |
| [no-ampersand-chaining](no-ampersand-chaining.md) | Never chain with `&&` in a Windows/MINGW agent shell; check exit codes explicitly |
| [oss-pr-quality-bar](oss-pr-quality-bar.md) | Only open upstream PRs that solve a real problem at 7/10 or better |
| [python-tooling-gotchas](python-tooling-gotchas.md) | importlib on non-.py paths, broken `.venv` after a Python uninstall |
| [reasoning-model-probe-token-starvation](reasoning-model-probe-token-starvation.md) | Tiny `maxTokens` on a reasoning model fakes a failure; probe with 200+ tokens |
| [research-with-fetch-not-browser](research-with-fetch-not-browser.md) | Research with fetch and search tools; keep browser automation for UI testing |
| [sonarcloud-gate-fails-on-duplication](sonarcloud-gate-fails-on-duplication.md) | Gate fails with 0 issues on duplicated-lines density; find it via the measures API |
| [stale-snapshot-worklists](stale-snapshot-worklists.md) | A snapshot worklist reports DONE when it drains; re-derive from live data each chunk |
| [subagent-denials-cannot-be-retried](subagent-denials-cannot-be-retried.md) | After a subagent denial, the main agent retrying the same outcome is blocked; do such edits in the main session |
| [verify-integration-auth-first](verify-integration-auth-first.md) | Confirm the exact auth method before writing integration code; after two auth errors debug auth only |
| [verify-subagent-numbers-before-publishing](verify-subagent-numbers-before-publishing.md) | Subagent figures are not measurements; re-measure against an independent formulation |
| [windows-bash-gotchas](windows-bash-gotchas.md) | CRLF in tool stdout, jq negation, base64, PowerShell vs MINGW paths, stale npm global prefix |
| [windows-mcp-stdio-cmd-c](windows-mcp-stdio-cmd-c.md) | Launch npx-based stdio MCP servers on Windows through `cmd /c npx` |
