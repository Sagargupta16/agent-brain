---
name: reasoning-model-probe-token-starvation
description: "Probing a reasoning model with a tiny maxTokens fakes a failure -- the budget goes to thinking and the visible text comes back empty; give liveness probes about 200+ tokens"
type: reference
source: "observed 2026-07-02 probing Claude models on AWS Bedrock after a model availability change"
created: 2026-07-02
modified: 2026-10-07
status: active
visibility: public
---

A liveness probe against a reasoning model with `maxTokens` of 20 to 30 burns the whole budget on internal thinking, stops on `max_tokens`, and returns empty visible text. It looks exactly like the model is broken.

**Why:** a probe "failed" on a model that was in fact working; only the token budget was wrong.

**How to apply:**

- Give liveness probes `maxTokens` of about 200 or more so real output can appear.
- Read the response, not just the text: an empty text with a valid `usage` block or `reasoningContent` is token starvation, not an outage.
- A 5xx (for example `InternalServerException`) is a real failure. A `ValidationException` on a base model id that needs an inference profile is a usage error, not an outage.

Related: [[bedrock-us-vs-global-profile-latency]].
