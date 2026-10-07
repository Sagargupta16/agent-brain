---
name: claude-desktop-bedrock-config-gotchas
description: "Claude Desktop and Claude Code on Bedrock -- where the profile config lives, why the Setup screen overwrites edits, model picker errors, and why an OpenAI-compatible gateway breaks data-retention settings"
type: reference
source: "observed 2026-07-05 and 2026-09-29 configuring Claude Desktop (third-party provider install) and Claude Code against AWS Bedrock"
created: 2026-07-05
modified: 2026-10-07
status: active
visibility: public
---

## Where the config lives

- The third-party-provider Desktop install keeps its state in `%LOCALAPPDATA%\Claude-3p\`, not `%APPDATA%\Claude` (the first-party install). Model profiles are `%LOCALAPPDATA%\Claude-3p\configLibrary\<uuid>.json`, one file per profile, and `_meta.json` field `appliedId` picks the active one.
- **The Setup screen keeps its own copy of the profile and overwrites outside edits when it saves.** Change model names in the Setup screen, or edit the file only with the app fully quit (tray, then Quit).

## A gateway that drops retention settings

- **Symptom:** `API Error: 400 data retention mode 'default' is not available for this model`, plus a retryable "Try sending your message again" banner.
- **Root cause:** the active profile had `inferenceProvider: "mantle"` (Bedrock's OpenAI-compatible gateway). The gateway proxies the call and does not forward the account's data-retention setting, so models that require it are refused. The same account worked when the request path was direct Bedrock `InvokeModel`.
- **Fix:** switch `appliedId` to a profile with `inferenceProvider: "bedrock"` and `us.`-prefixed model ids. The CLI has the same failure mode: do not set a gateway-routing env var such as `CLAUDE_CODE_USE_MANTLE=1` for Claude models. The gateway is fine for non-Claude models.
- First wrong guess, for the record: it looked like a first-party OAuth account needing its own retention setting. It was not; everything was already on Bedrock.

## Model picker errors (Code tab)

- **"Not in availableModels set by your Claude Code settings"** means the exact model id, including the `us.` vs `global.` prefix, is missing from `availableModels` in the Claude Code settings file. Add the exact id.
- **Two `inferenceModels` entries in one tier with `isFamilyDefault: true`** log "using the first flagged" on every start. Keep one default per tier.
- **A greyed row with an (i) icon** is the app disabling the model; the hover text gives the reason.
- **A typo in a model id** (for example `sonnent` for `sonnet`) only fails with `ValidationException` the moment someone picks that model. Proofread the list.
- **A nested `claude -p` from inside a Desktop session cannot borrow Desktop-managed Bedrock credentials**, so it cannot reproduce picker errors.

Related: [[claude-desktop-vm-service-not-running]], [[bedrock-us-vs-global-profile-latency]], [[verify-integration-auth-first]].
