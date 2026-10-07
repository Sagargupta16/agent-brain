---
name: bedrock-us-vs-global-profile-latency
description: "Measured Bedrock us. vs global. cross-region inference profile latency from Asia via us-east-1 -- no meaningful difference, so pick on data residency and availability"
type: reference
source: "measured 2026-09-29 with a ConverseStream probe via us-east-1 from a client on another continent, 10 alternating calls each"
created: 2026-09-29
modified: 2026-10-07
status: active
visibility: public
---

| Profile | TTFT median | Total median | Throughput |
| --- | --- | --- | --- |
| `us.` | 2.72 s | 6.91 s | 83.6 tok/s |
| `global.` | 2.88 s | 7.07 s | 79.5 tok/s |

Model: Claude Sonnet 5, streamed with `ConverseStream`, 10 alternating calls per profile.

**Why it matters:** there is no real latency difference; network round trip is a small slice of time-to-first-token. `global.` helps under regional capacity pressure and AWS claims it is about 10% cheaper (not checked against a bill). The trade-off is that `global.` may process prompts outside the US.

**How to apply:**

- Choose between `us.` and `global.` on data residency and model availability, not latency.
- When a probe "fails", rule out token starvation on reasoning models first, see [[reasoning-model-probe-token-starvation]].

Related: [[claude-desktop-bedrock-config-gotchas]].
