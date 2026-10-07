---
name: harness-audit
description: >-
  Audit the local Claude Code setup end to end and report before changing
  anything. Plugins installed vs enabled, MCP servers configured vs connected
  vs unauthenticated, skills installed vs actually invoked (counted from the
  transcripts), duplicate tool servers, hooks and whether any mirrored hook
  copies are byte-identical, brain index vs files, settings model vs the model
  actually running. Use when the user says "analyze my complete local claude
  setup", "list all plugins", "see all our skills that we use", "which skills
  we use", "dirty setup", "consolidate", "I installed some plugin, see and
  list all", or "why so many / commands". Read-only by default; every
  proposed change is stated as "X from A to B because C" and applied only on
  "do it", and it never removes plugins from a marketplace the user publishes
  or reads .credentials.json.
---

# harness-audit

Harness configuration tends to follow an install, forget, purge, reinstall
cycle: "remove all mcp or plugin that need auth and are not authed", "I see a
lot of / commands and unnecessary stuff, dirty setup", "disable never used and
fix dupes". A typical audit finds a burst of plugins installed in a few minutes
adding a hundred skill descriptions to every session, most user skills never
invoked, and the same MCP server loaded twice. This skill makes that audit
repeatable so the cycle stops.

## Read first

- Prior harness decisions in the brain: `brain recall harness`, `brain recall
  plugin`, `brain recall mcp` (what was already decided and why; do not
  re-litigate)
- Any note on marketplaces you publish: never remove plugins from your own
  public marketplace because you do not use them locally
- `~/.claude/CLAUDE.md` and the workspace `CLAUDE.md` Skills and Hooks
  sections (the documented state to diff against)

## Sources

| Layer | Where the truth is |
| --- | --- |
| Plugins | `~/.claude/plugins/installed_plugins.json` (installed, with `installedAt`), `~/.claude/settings.json` `enabledPlugins` (true/false), `~/.claude/plugins/known_marketplaces.json` |
| MCP servers | `~/.claude.json` `mcpServers` (global) and `.projects[<cwd>].mcpServers`; plugin-provided servers under `~/.claude/plugins/cache/*/*/.mcp.json`; live state from the session listing (connected, connecting, auth required, failed) |
| Skills | `~/.claude/skills/*/SKILL.md` (user), plugin skills in the cache, any retired-skills archive dir you keep, and the skills section of each CLAUDE.md |
| Invocations | `~/.claude/projects/*/*.jsonl`: count `"name":"Skill"` tool uses by skill, and `Base directory for this skill:` user turns; both undercount, report both |
| Hooks | `jq '.hooks' ~/.claude/settings.json`; scripts in `~/.claude/hooks/`; if you keep a checked-in source copy of the hooks elsewhere, the two copies must be byte-identical (`md5sum`) |
| Rules and memory | `~/.claude/rules/*.md`; `$AGENT_BRAIN_DIR/INDEX.md` (default `~/.agent-brain`) pointer lines vs files on disk; `brain lint` |
| Model | `settings.json` `model` and `availableModels` vs the model named in the session's own environment |

## Procedure

1. Inventory each layer into a table. Counts first, names second. Never print
   a token, key or header value; server names and transports only.
2. Cross-check:
   - plugins installed but absent from `enabledPlugins` (state unknown), and
     enabled plugins whose skills were never invoked in the transcripts
   - MCP servers provided by two plugins at once (duplicate tool schemas), and
     servers in an auth-required or failed state for more than one session
   - skills present on disk but not in any CLAUDE.md, and skills documented
     in CLAUDE.md but gone from disk with no archived copy
   - hook scripts that differ between mirrored locations, or hook events with
     no script
   - `INDEX.md` pointer count vs brain file count (`brain lint` reports both)
   - skills whose description is longer than 700 chars (each description loads
     into every session)
3. Rank findings: duplicate servers and dead auth first (they cost every
   session), then never-invoked plugins by skill count, then documentation
   drift, then cosmetic.
4. Propose, do not apply: for each finding one line `X from A to B because C`.
   Disabling a plugin means `enabledPlugins[key] = false`, never uninstall,
   never a marketplace change.
5. On "do it": apply with `jq` into a temp file, validate with `python -c
   "import json; json.load(...)"`, back up `settings.json` first, then diff key
   counts before and after. Re-run step 1 and show the delta.

## Output

```
| layer | count | notes |
| plugins installed / enabled / disabled | 60 / 26 / 34 | 12 installed within 6 minutes on <date> |
| MCP servers configured / connected / auth needed / failed | 4 / 9 / 5 / 6 | <server> provided twice |
| skills user / plugin / retired | 12 / ~105 / 14 | 7 user skills never invoked |
| hooks | 4 events, 5 scripts | all byte-identical |
| brain index | 45 / 45 | in sync |

findings, ranked:
1. <finding> -> propose: <X from A to B because C>
2. ...

invocations (all transcripts): <skill: count, ...>
```

## Must not

- Never read `~/.claude/.credentials.json`, `.env*`, or print any header,
  key or token value from any config file.
- Never uninstall or remove a plugin from a marketplace the user publishes;
  disable locally at most, and only on "do it".
- Never change `model`, `effortLevel`, `alwaysThinkingEnabled` or permission
  rules as part of an audit; report them, the user decides.
- Never edit `settings.json` without a dated backup and a JSON validity check.
- Never treat a low invocation count alone as grounds to remove a skill;
  skills work through their description line too. Report the count, state
  the inference, let the user choose.

## Non-goals

Creating or rewriting skills (a skill-authoring skill, if installed), adding
hooks (`update-config`, if available), MCP server authoring, memory
consolidation (`save-session` and `memory-router`).
