"""Pipe synthetic hook payloads through each hook script and check the exit codes. Needs bash and jq."""

import json
import os
import pathlib
import shutil
import subprocess
import sys

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"
# On Windows prefer Git Bash; System32 bash is WSL and cannot see this checkout.
GIT_BASH = (
    pathlib.Path(os.environ.get("ProgramFiles", "C:/Program Files"))
    / "Git"
    / "bin"
    / "bash.exe"
)
BASH = os.environ.get("HOOK_BASH") or (str(GIT_BASH) if GIT_BASH.exists() else "bash")
ENV = {
    **os.environ,
    "PATH": os.pathsep.join(
        [str(pathlib.Path.home() / "bin"), os.environ.get("PATH", "")]
    ),
}
DASH = chr(0x2014)
NO_VERIFY = "--no" + "-verify"

# block-dangerous.sh: (command, expected exit code). 2 = blocked, 0 = allowed.
BASH_CASES = [
    # Force-push to main or master, in every flag position and refspec form.
    ("git push --force origin main", 2),
    ("git push origin main --force", 2),
    ("git push -f origin master", 2),
    ("git push origin master -f", 2),
    ("git push --force-with-lease origin main", 2),
    ("git push origin main --force-with-lease", 2),
    ("git push --force-if-includes origin main", 2),
    ("git push origin +main", 2),
    ("git push origin +HEAD:main", 2),
    ("git push --force origin HEAD:refs/heads/main", 2),
    ("git push --mirror origin main", 2),
    ("git -C repo push --force origin main", 2),
    ("cd repo && git push origin main --force", 2),
    ("git push --force", 2),
    ("git push -f origin", 2),
    # Deleting main on the remote.
    ("git push origin --delete main", 2),
    ("git push origin :main", 2),
    # Pushes that are fine.
    ("git push origin main", 0),
    ("git push origin feat/hooks", 0),
    ("git push --force-with-lease origin feat/hooks", 0),
    ("git push origin +feat/hooks", 0),
    ('git commit -m "never git push origin main --force"', 0),
    # Hook bypass.
    (f"git commit {NO_VERIFY} -m x", 2),
    (f"git push {NO_VERIFY} origin feat/hooks", 2),
    ("git commit -n -m x", 2),
    ("git commit -am x", 0),
    (f'git commit -m "explain why {NO_VERIFY} is banned"', 0),
    # rm on a drive root or the home directory.
    ("rm -rf /", 2),
    ("rm -rf /*", 2),
    ("rm -rf ~", 2),
    ("rm -r ~/projects", 2),
    ('rm -rf "$HOME"', 2),
    (f'rm -rf "{pathlib.Path.home().as_posix()}"', 2),
    ("rm -rf build", 0),
    ("rm ~/notes.txt", 0),
    # Secret files read through Bash.
    ("cat .env", 2),
    ("cat ~/.ssh/id_ed25519", 2),
    ("cp .env backup.txt", 2),
    ("cat .env.example", 0),
    ('grep -rn ".env" src', 0),
    ("cat ~/.ssh/id_ed25519.pub", 0),
    # Warned, not blocked.
    ("git reset --hard", 0),
    # Dashes in outbound text.
    (f'git commit -m "a {DASH} b"', 2),
    (f'gh pr create --title "a {DASH} b"', 2),
    (f"echo 'a {DASH} b'", 0),
    ("git status", 0),
]

CASES = [
    ("block-dangerous.sh", {"tool_input": {"command": cmd}}, want)
    for cmd, want in BASH_CASES
] + [
    ("check-dashes.sh", {"tool_input": {"content": f"a {DASH} b"}}, 2),
    (
        "check-dashes.sh",
        {"tool_input": {"old_string": f"x {DASH}", "new_string": f"y {DASH}"}},
        0,
    ),
    ("check-dashes.sh", {"tool_input": {"content": "a -- b"}}, 0),
    ("precompact-save-reminder.sh", {"trigger": "auto"}, 0),
]

if not shutil.which("jq", path=ENV["PATH"]):
    sys.exit("jq not found; the hooks need it")
failed = 0
for script, payload, want in CASES:
    r = subprocess.run(
        [BASH, script],
        cwd=HOOKS,
        env=ENV,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    ok = r.returncode == want
    failed += not ok
    print(
        f"{'ok  ' if ok else 'FAIL'} {script} rc={r.returncode} want={want} {(r.stderr or r.stdout).strip()[:70]}"
    )
sys.exit(1 if failed else 0)
