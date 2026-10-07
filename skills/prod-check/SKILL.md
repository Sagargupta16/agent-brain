---
name: prod-check
description: >-
  Verify a deployment end to end from this machine, read-only first. Resolve
  the repo's deploy targets, pull the latest Vercel or Render or GitHub Pages
  deployment state and logs through the provider CLI or API (or Composio if
  installed) and gh, hit the live URL and confirm the expected route and
  redirects, read Neon and Cloudflare health without writing, and report one
  table of target, status, last deploy, error excerpt, suspected cause. Use
  when the user says "observe prod", "I merged it just observe prod", "is it
  deployed in prod", "deploy failed see and fix", "see neon vercel logs", "so
  everything good after main merge", or "it still redirecting why". Never
  writes to a production database, changes env vars, or redeploys without an
  explicit "do it", and never calls "deployed" from a green CI badge alone.
---

# prod-check

The usual ask after a merge is "merge it, then check the deploy logs, the
database and the CDN, is everything stable". `ship` hands off here. Green CI is
the merge authority, but "merged" is not "deployed": one live HTTP hit is the
proof.

## Read first

- Repo `CLAUDE.md` (deploy target section) and the workspace deployments doc,
  if one exists
- Your user-level secrets rules: some integration tools return a credential
  inline. A "get connection URI" tool (for example Composio
  `NEON_GET_PROJECT_CONNECTION_URI`) returns a live password; never call it
  from this skill. Health needs no connection string.
- Browser automation (Chrome DevTools, Playwright) is for testing the running
  app's UI, not for these checks.

## Targets and how each is checked

| Target | Status source | Live proof | Notes |
| --- | --- | --- | --- |
| Vercel | `vercel` CLI or Composio `VERCEL_*`: deployments list, build and runtime logs for the latest production deployment | `curl -sIL <url>` returns 200 on the expected route | check custom domains as well as the `*.vercel.app` URL |
| GitHub Pages | `gh api repos/<r>/pages` and the latest `pages-build-deployment` run | `curl -sIL https://<domain>/<app>/` follows the redirect chain to 200 | base path matters (`/<repo>/` on project sites) |
| Render | Render API or Composio `RENDER_*` service and deploy status | `curl` with one retry after 60s: free tier sleeps after 15 minutes, the first hit can 502 or take a minute | |
| Neon | Neon API or Composio `NEON_*` project and branch status, compute state, read-only row counts through the app's own read endpoint if one exists | not a URL; report compute active/idle and last activity | never the connection URI tool |
| Cloudflare | Cloudflare API or Composio `CLOUDFLARE_*` DNS records and R2 bucket listing, read-only | DNS answers match the expected target | |

## Procedure

1. Resolve targets: read the repo `CLAUDE.md` and the deployments doc; list
   every target and its expected live URL. If the repo has none, say "no
   deploy target" and stop.
2. Latest deploy: for each target pull the newest production deployment,
   its state (ready, error, building), its timestamp, and the commit it built.
   Compare that commit to `origin/main` HEAD; a stale commit means the merge has
   not deployed yet, which is a finding, not a failure.
3. Logs: on error or building, read the build log and the last 100 runtime
   log lines. Quote the first error line verbatim; do not paraphrase.
4. Live hit: `curl -sIL --max-time 30 <url>`. Record the final status code and
   the redirect chain. For apps with auth, hit a public route and a known 404
   to confirm the router is serving. For Render, retry once after 60s before
   calling it down.
5. Data layer: Neon compute state and, where the app exposes a read-only
   health or count endpoint, its response. No SQL against production from
   here.
6. Report the table. If everything is green, say so in one line and stop.
7. Fix mode only when the user says fix, "deploy failed see and fix", or "do
   it": patch the cause in the repo on a branch, hand to `ship`, then re-run
   steps 2 to 4 against the new deployment. Never fix by editing prod data,
   env vars or dashboard settings; print the exact console step for the user
   instead.

## Output

```
| target | status | last deploy (UTC) | commit vs main | live | error excerpt | suspected cause |
| vercel app.example.com | READY | 2026-09-22T11:41:02Z | match | 200 | - | - |
| render example-api | LIVE | 2026-09-21T09:02:14Z | behind by 2 | 502 then 200 after retry | - | free tier cold start |
| pages example.github.io/site | built | 2026-09-22T11:42:30Z | match | 301 -> 200 | - | - |

verdict: <all green | N of M targets need attention>
next: <exact command or console step, or "nothing">
```

## Must not

- Never write to a production database, never run UPDATE or DELETE anywhere
  from this skill, never call a tool that returns a connection string or key.
- Never change env vars, redeploy, roll back or promote a deployment without an
  explicit "do it" naming the target.
- Never report "deployed" without the live HTTP result; never report "healthy"
  from CI state alone.
- Never paste log lines that contain tokens, cookies or connection strings;
  keep the error line, redact the value.
- Never use Chrome DevTools or Playwright for the checks above; `curl` and the
  APIs are the proof, the browser is for UI verification when asked.

## Non-goals

Merging (that is `ship`), fixing CI (that is `gh-actions`), database
migrations (that is `db-ops`), performance profiling.
