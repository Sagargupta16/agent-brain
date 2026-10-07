#!/usr/bin/env python3
"""Deterministic checks for this repo, no LLM: run before every commit and in CI.

AB001 en or em dash          AB005 private leak word (from $AGENT_BRAIN_LEAKWORDS file)
AB002 secret-shaped string   AB006 brain page problem (bin/brain.py lint)
AB003 skill frontmatter      AB007 broken relative markdown link
AB004 absolute home path
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "bin"))
from brain import DASHES, SECRETS, Brain, parse_frontmatter  # type: ignore[import-not-found]  # noqa: E402

TEXT = {".md", ".py", ".sh", ".json", ".yml", ".yaml", ".cmd", ".txt", ""}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
HOME_PATH = re.compile(
    r"\b[A-Za-z]:[\\/]Users[\\/](?!\.\.\.)[\w.-]+|/c/Users/(?!\.\.\.)[\w.-]+|/home/(?!runner\b)[a-z][\w.-]*/|/Users/(?!Shared\b)[A-Z][\w.-]+/"
)
MD_LINK = re.compile(r"\]\((?!https?:|mailto:|#|\{\{)([^)\s]+)\)")


def files() -> list[Path]:
    out = []
    for p in ROOT.rglob("*"):
        if p.is_file() and not SKIP_DIRS.intersection(p.parts) and p.suffix in TEXT:
            out.append(p)
    return sorted(out)


def leak_words() -> list[str]:
    path = os.environ.get("AGENT_BRAIN_LEAKWORDS")
    if not path or not Path(path).exists():
        return []
    return [
        w.strip().lower()
        for w in Path(path).read_text(encoding="utf-8").splitlines()
        if w.strip() and not w.startswith("#")
    ]


def main() -> int:
    problems: list[str] = []
    words = leak_words()
    me = Path(__file__).resolve()
    for p in files():
        rel = p.relative_to(ROOT).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            if p != me and any(d in line for d in DASHES):
                problems.append(f"{rel}:{n} AB001 en or em dash; use -- or -")
            for label, rx in SECRETS:
                if rx.search(line):
                    problems.append(f"{rel}:{n} AB002 looks like a {label}")
            home = HOME_PATH.search(line) if p != me else None
            if home:
                problems.append(f"{rel}:{n} AB004 absolute home path {home.group(0)!r}")
            low = line.lower()
            for w in words:
                if w in low:
                    problems.append(f"{rel}:{n} AB005 private word {w!r}")
            if p.suffix == ".md":
                for target in MD_LINK.findall(line):
                    clean = target.split("#", 1)[0]
                    if clean and not (p.parent / clean).exists():
                        problems.append(f"{rel}:{n} AB007 broken link {target}")
        if p.name == "SKILL.md":
            meta, _ = parse_frontmatter(text)
            head = text.split("---", 2)[1] if text.startswith("---") else ""
            if meta.get("name") != p.parent.name:
                problems.append(
                    f"{rel}:1 AB003 name {meta.get('name')!r} must equal folder {p.parent.name!r}"
                )
            if not meta.get("description"):
                problems.append(f"{rel}:1 AB003 missing description")
            elif (
                not re.search(r"^description:\s*>-?\s*$", head, re.M)
                and ": " in meta["description"]
            ):
                problems.append(
                    f"{rel}:1 AB003 description has an unquoted ': '; use a folded >- block"
                )
    for sub in ("learnings", "playbooks"):
        for err in Brain(ROOT / "brain" / sub).lint():
            problems.append(f"brain/{sub}/{err} AB006")
    for line in problems:
        print(line)
    print(f"{len(files())} files checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
