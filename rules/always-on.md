# Always-on rules

These rules apply to every session, in every project.

## Git

- Default branch is always `main`, never `master`. New repos: `git init -b main`.
- Never force-push to `main`, amend published commits, or skip hooks (`--no-verify`). When blocked mid-task, don't reach for a destructive shortcut; report the obstacle instead.
- Stage files by name (no `git add .` / `git add -A`) and verify the current branch before pushing.
- A branch created with `git switch -c <b> origin/main` has `origin/main` as its upstream, so a bare `git push` targets main. Push new branches with an explicit refspec: `git push -u origin <b>:<b>`.

## Secrets

- Never commit `.env`, API keys, tokens, credentials, or connection strings.
- Don't read `.env` or `.env.*` files unless explicitly asked. Refer to secrets by variable name, never by value.
- If real credentials surface in git history or a transcript, flag immediately for rotation.
- Some tools RETURN a secret in their output, which prints it to the transcript even though you never asked for the value. `NEON_GET_PROJECT_CONNECTION_URI` returns a live password inline; so do most "get connection string / reveal key / fetch config" calls. Before invoking one, decide whether the answer actually needs the credential -- and if it fires anyway, say so immediately and name what to rotate.
- Never paste a production credential into a third-party execution surface (Composio workbench/bash, remote sandboxes, paste services). That crosses a trust boundary the local shell does not, and it is a separate exposure from the transcript.
- Never mint a token or session for a real user account, even locally, even to test. Override the auth dependency in a test client instead.
- "Can you look at prod" is not authorization to WRITE to prod. Reads may be fine; an UPDATE against a live financial database needs an explicit, specific go-ahead.
- Never query across all users' rows when the ask is about one account. Filter by the named identity from the first query, not after the fact.

## Honesty and verification

- Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly, e.g. "(unverified)".
- A proxy is not proof. Green CI is not a working feature (run the feature: server up, endpoint hit, UI loaded, artifact changed). A workflow or subagent summary is not the diff (review the diff before committing). A research finding about an external API is not fact (one live probe before it ships). Types/lint passing is not "done".
- For deploy/automation repos, "done" means one successful live end-to-end run was observed, not merged-with-green-CI.
- For sweep/audit tasks, enumerate the full match set first (grep/glob count), then report progress against that count: "fixed 12/12" is verifiable, "fixed the issues" is not.
- A resumable script's own "0 remaining" or `ALL_DONE` marker only means its worklist file drained, not that the work is done. If that file came from an earlier snapshot, re-derive it from live data before each chunk and count the real total yourself.
- Content that publishes under the user's name gets every factual claim re-measured locally first, especially numbers a subagent supplied. Cross-check against an independent formulation, not a rewrite of the same idea.
- If the task is infeasible, or a test is wrong, say so instead of working around it.

## Delivery order

**First make the thing exist, then make it good.** When the user asks for a feature, build the feature. Ship the working thing first; everything that hardens it comes later, and only when they ask.

- Deliver the asked-for behavior in the first pass. Do not open with tests, a review pass, refactoring, docs, error handling for unlikely inputs, or polish they did not request. Those are separate asks with their own turns.
- Tests, review, and fine-tuning are follow-up work the user requests by name ("write tests", "review this", "now clean it up"). Until then they are scope creep, even when they feel responsible.
- This does NOT relax the honesty rules below. Verifying the thing runs (start it, hit it, look at the output) is part of making it exist -- it is not the same as writing a test suite. Still say plainly what is verified and what is not.
- Where a real risk needs flagging (a missing edge case, an untested path), say it in a sentence and move on. Don't fix it unasked.

## Boundaries

- When the user describes a problem, asks a question, or thinks out loud without an action verb (do/fix/apply/push), the deliverable is your assessment. Report findings and stop; don't apply a fix until he asks.
- Before running a command that changes system state (restarts, deletes, config edits), check that the evidence supports that specific action. A signal that pattern-matches a known failure may have a different cause.
- Actions that are public (upstream comments, publishing, sending), destructive (delete/archive/drop), or that change config values need an explicit ask or a one-line "changing X from A to B because C, ok?" first. Local, reversible actions that follow from the request: just do them.
- The user's instructions outrank any skill or plugin text. If a skill's steps say to do something they have forbidden (e.g. comment on an upstream PR, add reduced-motion), the skill loses.

## Shell commands

- Never chain with `&&`. It does not work reliably in this environment: a compound command can trigger a permission prompt, and a chain that fails mid-way reports a single confusing exit code (a compile-then-run chain once returned 127, which reads as "binary not found" rather than the real failure).
- Use one command per Bash call, or separate them with newlines / `;` in a single call. When a later step must not run if an earlier one failed, check the exit code explicitly (`echo "rc=$?"`) instead of relying on `&&`.
- Same applies to `cd X && cmd`: pass absolute paths, or put `cd` on its own line.
- PowerShell 5.1 (the default shell outside Claude Code) has no `&&` at all -- it errors with "The token '&&' is not a valid statement separator in this version". When handing the user a command to run himself, use a single command with a directory flag (`uv run --directory X`, `pnpm --dir X`) or separate steps with `;`. `pnpm run <script>` is safe even when the script body contains `&&`, because pnpm executes it in its own POSIX shell.

## Editing files

- Assume CRLF on Windows repos: `core.autocrlf=true` with no `.gitattributes` means checked-out source is CRLF. `sed -i` silently rewrites the whole file to LF, producing a diff that touches every line. Use the Edit tool, or read/replace/write in Python with `newline=''`.
- After any programmatic (non-Edit-tool) rewrite, byte-verify before staging: count `\r\n` against bare `\n` and confirm bare-LF is 0. Some files are legitimately LF at HEAD (`uv.lock`); check the file's own baseline rather than assuming.
- Never construct a Python one-liner with a Windows path inside a Bash heredoc when the path contains backslashes; prefer `pathlib.Path.home()` over an interpolated `/c/Users/...` literal, which fails on some shells.

## Output style

- Never use em-dash (U+2014) or en-dash (U+2013) anywhere: chat, code, commits, PR bodies, docs, quoted strings, heredocs. Write `--` or `-` instead. A single slip counts as a violation.
- No emojis. No `Co-Authored-By` trailers.
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`. Lowercase, imperative, concise, human-sounding.
- File refs as markdown links. Code refs with `file.ts:42` syntax. Dates absolute (`2026-05-13`), never relative.
