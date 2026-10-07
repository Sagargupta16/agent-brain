---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/package.json"
---

# JS/TS code rules

- ESM (`import`/`export`), not CommonJS (`require`).
- Destructure imports when possible: `import { foo } from 'bar'`.
- React: functional components with hooks. No class components.
- Package manager: `pnpm` preferred.
- Prefer modern tools (Vite, Biome, Bun) when mature.
- Tests: match the repo's existing framework (Vitest, Jest, Playwright). Never introduce a new one.
