---
name: oss-pr-quality-bar
description: "Only open open-source PRs that solve a real problem at 7/10 quality or better; no self-promo list adds, no low-context AI PRs, no bundled multi-fix PRs"
type: feedback
source: "set 2026-04-17 after auditing a contributor's full upstream PR history"
created: 2026-04-17
modified: 2026-10-07
status: active
visibility: public
---

Only open an upstream PR if it scores 7/10 or higher on quality. Skip low-effort, low-impact contributions entirely.

**Why:** a PR-history audit showed a bimodal split. Substantive fixes to mature repos (Airflow, the Terraform AWS provider, AWS CDK, Feast and similar) rated 7 to 9 and built real reputation. Self-promotional awesome-list adds, portfolio listings and free-subdomain registrations rated 3 to 4, cluttered the contribution timeline and diluted the signal. A maintainer also rejected a low-context AI-generated PR outright as making no sense.

**How to apply:** before opening a PR, confirm ALL of these:

1. **Real problem:** a concrete bug, missing feature or broken doc, not a self-listing or cosmetic addition.
2. **Scope discipline:** one focused change per PR. Split unrelated fixes into separate PRs.
3. **Codebase understanding:** read the whole relevant module first. Check whether existing data sources, locals or flags already solve it. Look at closed PRs on similar topics. Trace the live entry point, not a dead duplicate.
4. **Evidence in the description:** reference the issue, show a concrete reproduction, explain why the approach fits the project's conventions.
5. **Mature target:** prefer repos with active maintainers and real users. A surgical fix in a 10K-star project beats a feature add in a 100-star one.

Do not open PRs in these categories:

- Awesome-list additions of your own projects.
- Portfolio, developer-list or custom-subdomain registrations counted as contributions.
- Docstring-only additions to mature repos.
- Bulk renames or reformats without an accompanying fix.
- AI-generated fixes you have not personally validated against the project's patterns.

When unsure, open an issue first asking whether the approach is welcome instead of building a speculative PR. If a maintainer pushes back, apologize, close, and do not argue.
