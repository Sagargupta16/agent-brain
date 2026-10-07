---
name: stack-decisions
description: "Default stack choices and the reasoning behind them -- package managers, frameworks, state, styling, storage, IaC, CI/CD, testing, and how to evaluate a new tool"
type: playbook
source: "ported from a private multi-repo workspace playbook"
created: 2026-10-07
modified: 2026-10-07
status: active
visibility: public
---

# Stack Decisions

Why the defaults are what they are. When asked "should we use X?" -- start here.

## Models (agent work)

- Strongest available model with extended thinking for the main loop.
- A faster, cheaper model for fast passes and subagents.
- On AWS Bedrock, use a regional cross-region inference profile and confirm the auth method (bearer token vs SigV4) before anything else.

## Package managers

- **JS**: `pnpm`. Faster, strict, content-addressed store. No `npm`/`yarn` in new repos.
- **Python**: `uv`. Fall back to `pip install --break-system-packages` only when `uv` cannot be used.
- **Go**: standard `go mod`.

## JS frameworks

- **Vite** for SPAs. Fast, simple, minimal config.
- **Next.js** only when SSR/SSG or edge is actually needed.
- **TypeScript strict** everywhere.

## Python frameworks

- **FastAPI** for APIs. Pydantic, async, OpenAPI auto-generated.
- **Typer** for CLIs.
- **pytest** for tests.

## FARM stack

FastAPI + React + MongoDB. The backend serves `/api/*`; the frontend is a separate Vite app.

## State management (React)

- **TanStack Query** -- server state.
- **useState / useReducer** -- local state.
- **Context** -- truly global, low-frequency.
- **Zustand** -- when Context causes render storms.
- No Redux in new code.

## Styling

- **Tailwind** -- default.
- **CSS modules** -- fallback.
- No styled-components / emotion in new code.

## Data storage

- **MongoDB** -- document-shaped data.
- **Postgres** -- when relational is clearly right.
- **SQLite** -- local or single-user apps.
- **DynamoDB** -- serverless AWS work.

## AWS

- **Amplify Gen2** -- serverless full-stack.
- **Terraform** -- everything else.
- **CDK** -- when the target project already uses it.

## CI/CD

- **GitHub Actions** by default.
- **Renovate** for dependency updates -- grouped, on a fixed monthly cadence.
- Deploy targets: GitHub Pages (static), Render (backends), Vercel (Next.js).

## Testing

- **Vitest** over Jest.
- **React Testing Library** for components.
- **Playwright** for E2E.
- **pytest** for Python.
- Match each repo's existing test framework.

## When to deviate

- Upstream forks -- **always match upstream**, regardless of these defaults.
- One-off scripts -- use whatever is fastest.
- Hackathon / spike -- the defaults still apply; a deviation needs a reason.

## When asked "should we adopt X?"

Consider:

1. Does it replace something already in the stack? What is the migration cost?
2. Is the community healthy? Releases in the last 6 months, active issues.
3. Is it a paradigm shift or an incremental improvement?
4. Who else maintains this code? If it is a solo project, flexibility is higher.

Default answer: **no, unless it is a clear win.** The stack works; novelty has a cost.
