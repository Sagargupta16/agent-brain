#!/usr/bin/env bash
# PreToolUse hook on Bash: block destructive or rule-breaking commands.
# Exit 2 = block (stderr is shown to Claude). Exit 0 = allow.
#
# Pure bash after the single jq call: each extra process (grep, $(...)) costs
# ~30 ms on Git Bash, and a PreToolUse hook that hits its timeout lets the
# command run unchecked.
#
# The command is split into words, so flag order does not matter:
# `git push origin main --force`, `git push origin +main` and
# `git push --force-with-lease origin HEAD:main` are all caught.
#
# No `set -u`: macOS ships bash 3.2, where expanding an empty array under
# `set -u` is an unbound-variable error.

CMD=$(jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$CMD" ] && exit 0

block() {
  echo "blocked: $1" >&2
  exit 2
}

# Em/en-dash ban in outbound text (commits, tags, PR/issue/release bodies, API
# payloads). Matched anywhere, so `cd repo; git commit -m ...` is covered too.
DASH=$'\xe2\x80\x93|\xe2\x80\x94'
OUTBOUND='(^|[^[:alnum:]_-])(git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+(commit|tag|notes)|gh[[:space:]]+(pr|issue|release|api|repo|gist))([[:space:]]|$)'
if [[ $CMD =~ $DASH ]] && [[ $CMD =~ $OUTBOUND ]]; then
  block "em-dash or en-dash (U+2013/U+2014) in commit/PR/comment text. Replace with -- or - and retry."
fi

# BARE: quoted text replaced by Q, so flags inside commit messages never match.
# PLAIN: quote characters dropped but text kept, so `cat ".env"` and
# `rm -rf "$HOME"` still match.
BARE=$CMD
while [[ $BARE =~ (\"[^\"]*\"|\'[^\']*\') ]]; do
  BARE=${BARE/"${BASH_REMATCH[1]}"/Q}
done
PLAIN=${CMD//\"/}
PLAIN=${PLAIN//\'/}

# Sets SPLIT: the command split into simple commands on ; & | ( ` and newlines.
split() {
  SPLIT=${1//\$(/$'\n'}
  SPLIT=${SPLIT//[;&|(\`]/$'\n'}
  SPLIT=${SPLIT//[<>]/ }
}

# Sets CI: index of the command word in tok[], skipping VAR=value and wrappers.
cmd_index() {
  CI=0
  while [ "$CI" -lt "${#tok[@]}" ]; do
    case ${tok[CI]} in
      *=* | sudo | command | exec | time | nohup | env | xargs | '{') CI=$((CI + 1)) ;;
      *) break ;;
    esac
  done
}

check_git() {
  local i=$1 sub="" t a dst force=0 del=0 nonopt=()
  for t in "${tok[@]:i+1}"; do
    [ "$t" = "--no-verify" ] && block "--no-verify bypasses git hooks. Fix the hook issue instead."
  done
  i=$((i + 1))
  while [ "$i" -lt "${#tok[@]}" ]; do
    t=${tok[i]}
    case $t in
      -C | -c) i=$((i + 2)) ;;
      -*) i=$((i + 1)) ;;
      *)
        sub=$t
        break
        ;;
    esac
  done
  case $sub in
    commit)
      for t in "${tok[@]:i+1}"; do
        [[ $t =~ ^-[[:alpha:]]*n[[:alpha:]]*$ ]] && block "git commit -n is --no-verify; it bypasses pre-commit hooks. Fix the hook issue instead."
      done
      ;;
    reset | checkout)
      for t in "${tok[@]:i+1}"; do
        [ "$t" = "--hard" ] && echo "warning: destructive git op. Verify intent before proceeding." >&2
      done
      ;;
    push)
      for t in "${tok[@]:i+1}"; do
        case $t in
          --force | --force-with-lease* | --force-if-includes | --mirror) force=1 ;;
          --delete | -d) del=1 ;;
          --*) ;;
          -*) [[ $t =~ ^-[[:alpha:]]*f ]] && force=1 ;;
          *) nonopt+=("$t") ;;
        esac
      done
      # nonopt[0] is the remote; the rest are refspecs.
      for a in "${nonopt[@]:1}"; do
        [[ $a == +* ]] && force=1
        [[ $a == :* ]] && del=1
        dst=${a#+}
        dst=${dst##*:}
        dst=${dst#refs/heads/}
        if [ "$dst" = main ] || [ "$dst" = master ]; then
          [ "$force" = 1 ] && block "force-push to main/master. Push to a feature branch or get explicit permission."
          [ "$del" = 1 ] && block "deleting main/master on the remote."
        fi
      done
      if [ "$force" = 1 ] && [ "${#nonopt[@]}" -le 1 ]; then
        block "force-push without an explicit branch could hit main. Name it: git push --force-with-lease origin <branch>."
      fi
      ;;
  esac
}

check_rm() {
  local i=$1 t recursive=0 targets=()
  for t in "${tok[@]:i+1}"; do
    case $t in
      --recursive) recursive=1 ;;
      --*) ;;
      -*) [[ $t =~ [rR] ]] && recursive=1 ;;
      *) targets+=("$t") ;;
    esac
  done
  for t in "${targets[@]}"; do
    t=${t%\*}
    [ "$t" != / ] && t=${t%/}
    case $t in
      / | /c | /C | [cC]: | [cC]:\\)
        block "rm on a drive root."
        ;;
      '~'*)
        [ "$recursive" = 1 ] && block "rm -r on a home-directory path (~). Use the absolute path of the exact folder."
        ;;
      '$HOME' | '${HOME}')
        block "rm on the home directory itself."
        ;;
    esac
    for h in "${HOMES[@]}"; do
      [ "$t" = "$h" ] && block "rm on the home directory itself."
    done
  done
}

# The home directory as POSIX shells, Git Bash and Windows spell it.
HOMES=("${HOME%/}")
if [ -n "${USERPROFILE:-}" ]; then
  HOMES+=("$USERPROFILE" "${USERPROFILE//\\//}")
fi

# Secret files: Read() deny rules in Claude Code settings cover the file tools
# but not Bash, so the same paths are blocked here.
SECRET='(^|[/@=])(\.env(\.[[:alnum:]_.-]+)?|\.netrc|\.npmrc|\.pypirc|\.git-credentials|\.credentials\.json|id_(rsa|ed25519|ecdsa|dsa)|[^/]*\.(pem|ppk))$|(^|[/@=])\.(ssh|aws)(/|$)|(^|/)gh/hosts\.yml$'
SAFE='\.env\.(example|sample|template|dist|defaults)$|\.pub$'

check_secrets() {
  local i=$1 w=$2 t skip=0 n pos=()
  case $w in
    grep | egrep | fgrep | rg | sed | awk | gawk | jq | yq) skip=1 ;; # first positional is the pattern
  esac
  for t in "${tok[@]:i+1}"; do
    [[ $t == -* ]] && continue
    pos+=("$t")
  done
  n=${#pos[@]}
  case $w in
    cp | scp | rsync) n=$((n - 1)) ;; # last positional is the destination
  esac
  [ "$n" -le "$skip" ] && return
  for t in "${pos[@]:skip:n-skip}"; do
    if [[ $t =~ $SECRET ]] && ! [[ $t =~ $SAFE ]]; then
      block "reads a secret file ($t) via Bash; refer to secrets by variable name. If the user explicitly asked for it, tell them and let them run it."
    fi
  done
}

split "$BARE"
while IFS= read -r seg; do
  read -ra tok <<<"$seg"
  [ "${#tok[@]}" -eq 0 ] && continue
  cmd_index
  [ "$CI" -ge "${#tok[@]}" ] && continue
  w=${tok[CI]##*/}
  [ "${w%.exe}" = git ] && check_git "$CI"
done <<<"$SPLIT"

split "$PLAIN"
while IFS= read -r seg; do
  read -ra tok <<<"$seg"
  [ "${#tok[@]}" -eq 0 ] && continue
  cmd_index
  [ "$CI" -ge "${#tok[@]}" ] && continue
  w=${tok[CI]##*/}
  w=${w%.exe}
  case $w in
    rm) check_rm "$CI" ;;
    cat | head | tail | less | more | bat | tac | nl | strings | xxd | od | hexdump | base64 | \
      grep | egrep | fgrep | rg | sed | awk | gawk | cut | sort | uniq | diff | cmp | comm | paste | \
      jq | yq | cp | scp | rsync | tar | zip | 7z | curl | source | . | gc | Get-Content)
      check_secrets "$CI" "$w"
      ;;
  esac
done <<<"$SPLIT"

exit 0
