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
CASES = [
    (
        "block-dangerous.sh",
        {"tool_input": {"command": "git commit --no" + "-verify -m x"}},
        2,
    ),
    (
        "block-dangerous.sh",
        {"tool_input": {"command": "git push --force origin main"}},
        2,
    ),
    ("block-dangerous.sh", {"tool_input": {"command": "rm -rf ~"}}, 2),
    ("block-dangerous.sh", {"tool_input": {"command": "git status"}}, 0),
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
