---
name: verify-integration-auth-first
description: "Before writing integration code for an external service, confirm the exact auth method (OAuth vs API key vs SigV4 vs bearer); after two auth errors, debug auth only"
type: feedback
source: "derived 2026-04 to 2026-06-10 from five or more sessions that built the wrong auth flow first"
created: 2026-06-10
modified: 2026-10-07
status: active
visibility: public
---

Before writing integration code for any external service (AWS Bedrock, Stripe, an OAuth provider, a tool-router platform), verify the exact auth method FIRST. State the auth flow and confirm it before scaffolding.

**Why:** the single most expensive friction pattern. Several sessions burned rounds building the wrong approach: bearer token vs SigV4, API key vs OAuth, static key vs rotating credential, restricted vs secret key.

**How to apply:**

- First action in any integration task: "Confirming auth flow, SERVICE uses METHOD. Proceeding?"
- If an auth error fires twice, STOP and debug auth. Do not iterate on other causes first.
- Quick triage: 401/403 means token or credentials; 404 on a model id means wrong region or model slug.
- For Bedrock specifically, check `CLAUDE_CODE_USE_BEDROCK`, `AWS_REGION` and any base-URL override before anything else.

Related: [[agent-execution-patterns]], [[claude-desktop-bedrock-config-gotchas]].
