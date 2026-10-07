---
name: aws-ops
description: >-
  Reads-first AWS helper for the user's personal or consulting accounts.
  Access keys (local profiles, IAM, retiring one), unexpected S3 bills (Cost
  Explorer, bucket metrics, CloudTrail), least-privilege IAM for a named
  task, Bedrock model and quota checks on the inference profile that works
  for the account, Bedrock Mantle endpoints, and the runbook prompt for an
  agent holding AWS credentials. Use when the user says "from where to
  delete access keys?", "what access keys do we have saved in aws here?",
  "if I give you a temporary access key can you find out?", or "also include
  bedrock mantle". Never asks for or echoes a key or token, creates or
  deletes a resource without an explicit ask, or uses an inference profile
  recorded as broken for the account.
---

# aws-ops

Asks about AWS itself, apart from any repo: "from where to delete access
keys?", "what access keys do we have saved here?", someone's surprise S3 bill,
and "give the exact prompt for what needs to be done" for an agent that holds
the credentials. Reads run freely; anything that creates, changes or deletes
waits for an explicit ask naming the resource.

## Read first

- Your always-on rules, if you keep them. Secrets: keys and tokens by
  variable name only; a pasted credential is flagged for rotation, never used
- Account facts in the brain (`brain recall bedrock`, `brain recall aws`):
  auth method (bearer token vs SigV4 vs profile), which inference profile
  prefix works (`us.`, `eu.`, `global.`) and which is known-broken, the region
  per model family, and any data-retention setting a gateway must preserve.
  Record new ones with `brain remember`.
- Lessons for any account: confirm the auth method before any integration
  step; probe reasoning models with `maxTokens >= 200` (a 500 is a fault,
  empty text with usage is token starvation); real Bedrock spend lives in AWS,
  not a vendor dashboard; Bedrock Mantle (OpenAI-compatible gateway) paths
  differ per region and model family, so verify live, and never route Claude
  through it if it drops a retention setting the account needs

## Procedure

1. Identity first, always: `aws sts get-caller-identity` and `aws configure
   list` (key id masked, its source, the region). Say which account and
   identity the session is in; a work or client account is never touched from
   a personal identity.
2. Access keys, local: `aws configure list-profiles`; `ls ~/.aws` for which
   files exist; `env | grep -oE '^AWS_[A-Z_]+'` for variable names. Never open
   `~/.aws/credentials` or an `.env`; the profile name is the answer.
3. Access keys, IAM: `aws iam list-access-keys --user-name <user>` and
   `aws iam get-access-key-last-used --access-key-id <id>`. Retire in two
   steps and only on ask: `aws iam update-access-key --status Inactive
   --access-key-id <id> --user-name <user>`, wait for the user to confirm
   nothing broke, then `aws iam delete-access-key` with the same arguments.
   Root keys are console only (account menu, Security credentials). Verify:
   `list-access-keys` no longer shows the id.
4. "If I give you a temporary access key can you find out?": yes, without
   pasting it. The user runs `aws configure --profile temp` in their own
   terminal and types the values there, says done, and every read below runs
   with `--profile temp`. The key never enters the transcript; the user
   deletes it after.
5. Unexpected S3 bill: `aws ce get-cost-and-usage --time-period
   Start=<first of month>,End=<today> --granularity MONTHLY --metrics
   UnblendedCost --group-by Type=DIMENSION,Key=SERVICE`, then filtered to S3
   with `--group-by Type=DIMENSION,Key=USAGE_TYPE` (storage vs requests vs data
   transfer); `aws s3api list-buckets`; per bucket `get-bucket-location` and
   `get-bucket-policy-status`; CloudWatch `AWS/S3` `BucketSizeBytes` daily;
   `aws cloudtrail lookup-events --lookup-attributes
   AttributeKey=EventSource,AttributeValue=s3.amazonaws.com` for who created
   what. On a "nothing created" account the usual causes, in order: a leaked
   key used by someone else (`iam list-users`, recent `list-access-keys`), a
   public bucket serving requests, CloudTrail data events writing to S3. Cost
   Explorer needs enabling once and lags about 24 hours; say so.
6. Least privilege: list the exact API calls the task makes, write
   `policy.json` with those actions and resource ARNs, run `aws accessanalyzer
   validate-policy --policy-document file://policy.json --policy-type
   IDENTITY_POLICY`, and stop. `aws iam create-policy` only on "do it".
7. Bedrock: `aws bedrock list-inference-profiles --region <region>` filtered
   on the model name, `aws bedrock list-foundation-models --by-provider
   anthropic`, `aws service-quotas list-service-quotas --service-code bedrock`.
   Liveness: `aws bedrock-runtime converse --model-id <profile>.anthropic.<model>
   --messages '[{"role":"user","content":[{"text":"reply ALIVE"}]}]'
   --inference-config maxTokens=300 --region <region>` with the account's
   auth (for example `AWS_BEARER_TOKEN_BEDROCK`) set in the shell. Spend: Cost
   Explorer filtered to Amazon Bedrock plus CloudWatch `AWS/Bedrock`
   `InputTokenCount` and `OutputTokenCount` by ModelId; `cost = in / 1e6 *
   in_price + out / 1e6 * out_price` with prices fetched live (the
   `claude-api` skill or the pricing page), never from memory.
8. Runbook prompt for an agent with the user's credentials: identity check
   first, region stated, read phase with exact commands, a stop-and-report
   gate before any create or delete, the output table below, and the Mantle
   endpoint table when asked to include Bedrock Mantle. Credentials are named
   (`AWS_PROFILE`, `AWS_BEARER_TOKEN_BEDROCK`, `OPENAI_API_KEY`), never pasted
   into the prompt.
9. Console-only steps (root keys, billing preferences, budgets) are printed as
   numbered clicks; the user does them and says done, then step 1 or 3
   re-verifies.

## Output

```
identity: <arn from sts, account id masked to last 4> | region <r> | profile <p>

| question | evidence (command) | result | next step (yours or mine) |
| keys in use | aws iam list-access-keys | 2 keys, one unused since <YYYY-MM-DD> | yours: confirm, then I run update-access-key Inactive |

console steps for you: <numbered, or "none">
unverified: <what could not be read and why>
```

## Must not

- Never ask for, accept in chat, or echo an access key, secret, session token
  or bearer token; if one is pasted, say so, name what to rotate, and proceed
  through a profile the user configures themselves.
- Never `cat ~/.aws/credentials`, `.env`, or a desktop app config env block;
  bearer tokens surface there in plaintext.
- Never create, modify or delete an AWS resource, policy, key or budget
  without an explicit ask naming it; reads are always fine.
- Never use an inference profile or gateway the brain records as broken for
  this account.
- Never touch a work or client account from a personal identity, or store
  its details in the brain.
- Never quote model pricing or IDs from memory.
- Never chain commands with `&&`; one command per call.

## Non-goals

Terraform in the user's IaC repos (normal coding there), Vercel, Neon and
Render checks (`prod-check`), Claude Code settings and model switching
(`update-config`, if available), Bedrock image and video generation (a
Bedrock MCP server, if installed).
