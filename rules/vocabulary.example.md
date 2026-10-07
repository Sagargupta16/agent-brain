# Prompt vocabulary (example)

One user's shorthand, kept as a worked example. Copy it, then rewrite each line in
your own words: an agent that knows what your `etc` or `just tell` means stops
asking and stops over-reaching.

## Scope signals

- **`just tell`** = answer only, no code, no file edits, no tool calls beyond what's needed to answer. Wins over any surrounding execution-sounding verbs.
- **`just do X`** / **`just fix X`** / **`just these`** = narrow execution, do not expand scope, do not update sibling files unless they are directly named.
- **`Do it`** / **`Go ahead`** / **`Push it`** / **`Do whatever best you feel`** / **`Continue`** = full autonomy, skip "should I proceed" questions.
- **`dig`** / **`research`** / **`dig on internet`** = deep research with REAL web searches and links, not training memory. The user checks.
- **`study`** = thorough codebase read before suggesting anything. **`find location`** / **`see where`** = locate, don't modify. **`see X`** (imperative) = investigate X and act on findings.
- **`just do 1`** / **`Do 2, 3, 4`** = numbered subset of your last list; do exactly those.
- **`a to z`** / **`each and all`** / **`each and every`** / **`every single`** = comprehensive audit, no early-stop at the first few matches.
- **Composite asks** ("do X and Y and Z etc") = parse every named item and execute in order. Don't ask which first. `also` chains mid-message are real tasks, not asides.
- **`no X for now`** = explicit temporary exclusion. Respect it; don't sneak X back in.
- **`1 by 1`** / **`1 at a time`** = stepwise mode: one step, then WAIT for confirmation before the next.

## Tone interpretation

- **`etc`** at end of a question = "and the related obvious stuff too". Expand to sibling files, adjacent settings, related commands. Not vague -- it's a fill-in-the-blanks marker.
- **Typos are expected** (`jsut`, `noty`, `whjat`, `cowrk`). Understand the intent anyway. Do not ask to re-type.
- **`??` / `???` / `!!`** = emphasis/intensity, not literal confusion. Don't over-qualify the answer.
- **ALL-CAPS words mid-sentence** = emphasis, not shouting. Treat as underlined.
- **No greetings, no preambles** -- The user starts mid-thought. Match that energy in replies: lead with the answer, no "Great question!".
- **`kinda`** / **`or something`** = approximate spec; fill in details from context, don't ask for precision.
- **Positional answers** ("1 keep 2 kill", "A but no PII, B yes") map 1:1 to your last numbered list. Never re-ask.

## Execution defaults

- When the user asks to DO something (apply, rename, merge, deploy), take action immediately on the named thing. Do not produce plans or analysis unless explicitly asked for a plan first.
- Ambiguity precedence, WHAT vs HOW: if the WHAT is unresolvable (a proper noun that could name several repos or projects), ask one clarifying question before executing; a misread here can archive the wrong repo. If only the HOW is approximate (`kinda`, `or something`, missing details), fill in from context and state the assumption inline ("Assuming X, correct me if wrong"). For destructive or public actions, unresolved ambiguity always means ask first.
- If the request is "EXECUTION session", skip all planning overhead and take action directly.
- Act on the named scope only. One-line scope echo before integration or multi-surface work ("fetch images only, no account actions") keeps adjacent things out.

## Verification loop (the user audits claims)

- **`done <X> now <Y>`** / **`done now test!`** = the user's manual console step (dashboard/DNS/OAuth) is complete; verify it LIVE and continue immediately. This relay loop is the standard pattern for external-service setup.
- **`now test!`** / **`now see!`** = run live verification now (real API call, server up). A file diff is not proof.
- **`You sure?`** / **`all done as i told???`** = back the answer with evidence (commands run, output seen), never just restate intent.
- Merging is gated on green CI and CLAUDE checks it: "see all checks passed if so merge it". After merge, confirm deployment succeeded.
- One PR per work stream until merged. Follow-ups go to the same branch, never a second PR.

## Hard "don't" rules (each cost a correction)

- Don't remove existing UI/content (footers, copyright, credits) during refactors.
- Don't change config values silently -- explain and ask first.
- Don't add prefers-reduced-motion or tone down animations on web UI -- the user wants motion visible.
- After 2 failed attempts at a calculation, STOP iterating; list the formulas/assumptions and let the user correct.
- Before creating new assets (skills, configs), search for existing ones first.
- `latest` everywhere: outdated deps are defects; `legacy`/`deprecated`/`stale`/`unnessary` things get purged, not kept for compat.
- Anything web-facing must be mobile friendly -- most users are on phones.
- **`grind with yourself`** = iterate autonomously against your own quality bar before showing results; a timid diff after a revamp ask is a failure.
