#!/usr/bin/env python3
"""brain -- a markdown memory your agents share.

One fact per file, with its source. Facts are corrected or withdrawn, never
silently overwritten. Every agent reads the same folder: Claude Code, Codex and
Kiro through the CLI or the stdio MCP server (`brain mcp`).

Folder: --dir, else $AGENT_BRAIN_DIR, else ~/.agent-brain.
Standard library only (Python 3.10+).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "0.1.0"
TYPES = ("user", "feedback", "project", "reference", "playbook")
STATUSES = ("active", "corrected", "withdrawn")
VISIBILITY = ("private", "public")
KEY_ORDER = (
    "name",
    "description",
    "type",
    "source",
    "created",
    "modified",
    "status",
    "visibility",
    "supersedes",
    "superseded_by",
    "withdrawn",
    "reason",
)
SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
LINK = re.compile(r"\[\[([a-z0-9][a-z0-9_-]*)(?:[|#][^\]]*)?\]\]")
DASHES = (chr(0x2013), chr(0x2014))
SECRETS = [
    ("aws access key", re.compile(r"\bA(?:KIA|SIA)[0-9A-Z]{16}\b")),
    (
        "github token",
        re.compile(
            r"\b(?:ghp|gho|ghs|ghu)_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{40,}"
        ),
    ),
    ("api key", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("bearer token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{24,}")),
]


def today() -> str:
    return dt.date.today().isoformat()


# ---------- pages ----------


@dataclass
class Page:
    path: Path
    meta: dict[str, str] = field(default_factory=dict)
    body: str = ""

    @property
    def slug(self) -> str:
        return self.path.stem

    @property
    def status(self) -> str:
        return self.meta.get("status", "active")

    @property
    def type(self) -> str:
        return self.meta.get("type", "reference")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Flat `key: value` frontmatter; one nested level (Claude's `metadata:`) is flattened."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}, text
    meta: dict[str, str] = {}
    folded_key, folded_parts, parent = None, [], None
    for raw in lines[1:end]:
        if folded_key is not None:
            if raw.startswith((" ", "\t")) and raw.strip():
                folded_parts.append(raw.strip())
                continue
            meta[folded_key] = " ".join(folded_parts)
            folded_key, folded_parts = None, []
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indented = raw.startswith((" ", "\t"))
        key, sep, value = raw.strip().partition(":")
        if not sep:
            continue
        key, value = key.strip(), value.strip()
        if not indented:
            parent = None
        if value == "" and not indented:
            parent = key
            continue
        if value in (">-", ">", "|", "|-"):
            folded_key = key
            continue
        if indented and parent and parent != "metadata":
            key = f"{parent}.{key}"
        meta[key] = value.strip("\"'")
    if folded_key is not None:
        meta[folded_key] = " ".join(folded_parts)
    return meta, "\n".join(lines[end + 1 :]).lstrip("\n")


def render(meta: dict[str, str], body: str) -> str:
    keys = [k for k in KEY_ORDER if meta.get(k)] + sorted(
        k for k in meta if k not in KEY_ORDER and meta[k]
    )
    head = []
    for k in keys:
        v = meta[k]
        head.append(
            f"{k}: {json.dumps(v) if ': ' in v or v.startswith(('[', '{', '#', '*')) else v}"
        )
    return "---\n" + "\n".join(head) + "\n---\n\n" + body.strip() + "\n"


class Brain:
    def __init__(self, root: Path):
        self.root = root

    def files(self) -> list[Path]:
        if not self.root.exists():
            return []
        skip = {"INDEX.md", "MEMORY.md", "README.md"}
        return sorted(
            p
            for p in self.root.rglob("*.md")
            if p.name not in skip and ".git" not in p.parts
        )

    def pages(self) -> list[Page]:
        out = []
        for p in self.files():
            meta, body = parse_frontmatter(p.read_text(encoding="utf-8"))
            out.append(Page(p, meta, body))
        return out

    def find(self, slug: str) -> Page:
        for page in self.pages():
            if page.slug == slug or page.meta.get("name") == slug:
                return page
        raise SystemExit(f"brain: no page named {slug!r} in {self.root}")

    def write(self, page: Page) -> None:
        page.path.parent.mkdir(parents=True, exist_ok=True)
        page.path.write_text(
            render(page.meta, page.body), encoding="utf-8", newline="\n"
        )

    # ---- verbs ----

    def recall(
        self, query: str, k: int = 5, include_inactive: bool = False
    ) -> list[dict]:
        pages = [p for p in self.pages() if include_inactive or p.status == "active"]
        if not pages:
            return []
        tok = lambda s: re.findall(r"[a-z0-9]+", s.lower())  # noqa: E731
        docs = []
        for p in pages:
            head = tok(p.meta.get("name", p.slug) + " " + p.meta.get("description", ""))
            docs.append(head * 3 + tok(p.body))  # title and description weigh triple
        n = len(docs)
        avg = sum(map(len, docs)) / n
        df: dict[str, int] = {}
        for d in docs:
            for t in set(d):
                df[t] = df.get(t, 0) + 1
        terms = tok(query)
        scored = []
        for p, d in zip(pages, docs):
            score = 0.0
            for t in terms:
                f = d.count(t)
                if not f:
                    continue
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                score += idf * f * 2.2 / (f + 1.2 * (0.25 + 0.75 * len(d) / avg))
            if score > 0:
                scored.append((score, p))
        scored.sort(key=lambda x: -x[0])
        return [
            {
                "name": p.slug,
                "score": round(s, 3),
                "type": p.type,
                "status": p.status,
                "description": p.meta.get("description", ""),
                "source": p.meta.get("source", ""),
                "path": str(p.path),
                "body": p.body.strip(),
            }
            for s, p in scored[:k]
        ]

    def remember(
        self,
        name: str,
        description: str,
        body: str,
        type_: str = "reference",
        source: str = "",
        visibility: str = "private",
        supersedes: str = "",
    ) -> Page:
        if not SLUG.match(name):
            raise SystemExit(f"brain: name must be kebab-case, got {name!r}")
        if type_ not in TYPES:
            raise SystemExit(f"brain: type must be one of {TYPES}")
        if visibility not in VISIBILITY:
            raise SystemExit(f"brain: visibility must be one of {VISIBILITY}")
        path = self.root / f"{name}.md"
        if path.exists():
            raise SystemExit(
                f"brain: {name} exists; use `brain correct {name} ...` to replace it"
            )
        problems = scan_text(description + "\n" + body)
        if problems:
            raise SystemExit("brain: refusing to save, " + "; ".join(problems))
        meta = {
            "name": name,
            "description": description,
            "type": type_,
            "source": source or "unspecified",
            "created": today(),
            "modified": today(),
            "status": "active",
            "visibility": visibility,
        }
        if supersedes:
            meta["supersedes"] = supersedes
        page = Page(path, meta, body)
        self.write(page)
        self.index()
        return page

    def correct(
        self, old: str, name: str, description: str, body: str, source: str = ""
    ) -> Page:
        prev = self.find(old)
        if prev.status != "active":
            raise SystemExit(f"brain: {old} is already {prev.status}")
        new = self.remember(
            name,
            description,
            body,
            prev.type,
            source,
            prev.meta.get("visibility", "private"),
            supersedes=prev.slug,
        )
        prev.meta.update(status="corrected", superseded_by=new.slug, modified=today())
        self.write(prev)
        self.index()
        return new

    def forget(self, slug: str, reason: str) -> Page:
        page = self.find(slug)
        page.meta.update(
            status="withdrawn",
            withdrawn=today(),
            reason=reason or "unspecified",
            modified=today(),
        )
        self.write(page)
        self.index()
        return page

    def index(self) -> Path:
        groups: dict[str, list[Page]] = {t: [] for t in TYPES}
        for p in self.pages():
            if p.status == "active":
                groups.setdefault(p.type, []).append(p)
        lines = [
            "# Brain index",
            "",
            "Generated by `brain index`. One line per active page.",
            "",
        ]
        for t, pages in groups.items():
            if not pages:
                continue
            lines += [f"## {t.capitalize()}", ""]
            for p in sorted(pages, key=lambda x: x.slug):
                rel = p.path.relative_to(self.root).as_posix()
                lines.append(f"- [{p.slug}]({rel}) - {p.meta.get('description', '')}")
            lines.append("")
        out = self.root / "INDEX.md"
        self.root.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
        return out

    def lint(self) -> list[str]:
        errors = []
        pages = self.pages()
        slugs = {p.slug for p in pages}
        for p in pages:
            rel = p.path.relative_to(self.root).as_posix()
            if not p.meta:
                errors.append(f"{rel}: no frontmatter")
                continue
            for key in ("name", "description"):
                if not p.meta.get(key):
                    errors.append(f"{rel}: missing {key}")
            if p.meta.get("name") and p.meta["name"].replace("_", "-") != p.slug.replace("_", "-"):
                errors.append(f"{rel}: name {p.meta['name']!r} does not match filename")
            if p.type not in TYPES:
                errors.append(f"{rel}: type {p.type!r} not in {TYPES}")
            if p.status not in STATUSES:
                errors.append(f"{rel}: status {p.status!r} not in {STATUSES}")
            for ref in ("supersedes", "superseded_by"):
                if p.meta.get(ref) and p.meta[ref] not in slugs:
                    errors.append(
                        f"{rel}: {ref} points at missing page {p.meta[ref]!r}"
                    )
            for target in LINK.findall(p.body):
                if target.strip() not in slugs:
                    errors.append(f"{rel}: broken link [[{target}]]")
            for problem in scan_text(p.path.read_text(encoding="utf-8")):
                errors.append(f"{rel}: {problem}")
        return errors

    def export(self, dest: Path) -> int:
        count = 0
        for p in self.pages():
            if p.status == "active" and p.meta.get("visibility") == "public":
                target = dest / p.path.relative_to(self.root)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p.path, target)
                count += 1
        Brain(dest).index()
        return count


def scan_text(text: str) -> list[str]:
    out = [f"contains a {label}" for label, rx in SECRETS if rx.search(text)]
    if any(d in text for d in DASHES):
        out.append("contains an en or em dash; use -- or -")
    return out


# ---------- MCP (stdio, JSON-RPC 2.0, newline-delimited) ----------

TOOLS = [
    {
        "name": "recall",
        "description": "Search the brain for facts relevant to a query. Call before answering anything the user may have told you before.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "remember",
        "description": "Save one durable fact with its source. Kebab-case name. Refuses secrets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "body": {"type": "string"},
                "type": {"type": "string", "enum": list(TYPES)},
                "source": {"type": "string"},
                "visibility": {
                    "type": "string",
                    "enum": list(VISIBILITY),
                    "default": "private",
                },
            },
            "required": ["name", "description", "body", "source"],
        },
    },
    {
        "name": "correct",
        "description": "Replace a fact that turned out wrong. The old page is kept and marked corrected.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "old": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "body": {"type": "string"},
                "source": {"type": "string"},
            },
            "required": ["old", "name", "description", "body"],
        },
    },
    {
        "name": "forget",
        "description": "Withdraw a fact. It stays on disk for history but is no longer recalled.",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "reason": {"type": "string"}},
            "required": ["name", "reason"],
        },
    },
]


def call_tool(brain: Brain, name: str, args: dict) -> str:
    if name == "recall":
        return json.dumps(brain.recall(args["query"], int(args.get("k", 5))), indent=1)
    if name == "remember":
        p = brain.remember(
            args["name"],
            args["description"],
            args["body"],
            args.get("type", "reference"),
            args.get("source", ""),
            args.get("visibility", "private"),
        )
        return f"saved {p.path}"
    if name == "correct":
        p = brain.correct(
            args["old"],
            args["name"],
            args["description"],
            args["body"],
            args.get("source", ""),
        )
        return f"saved {p.path}; {args['old']} marked corrected"
    if name == "forget":
        p = brain.forget(args["name"], args.get("reason", ""))
        return f"withdrew {p.slug}"
    raise ValueError(f"unknown tool {name}")


def serve_mcp(brain: Brain) -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid, method = msg.get("id"), msg.get("method", "")
        if mid is None:
            continue  # notification
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": msg.get("params", {}).get(
                        "protocolVersion", "2025-06-18"
                    ),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "agent-brain", "version": VERSION},
                    "instructions": f"Shared memory at {brain.root}. recall before answering; remember durable facts with a source.",
                }
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                params = msg.get("params", {})
                try:
                    text, is_error = (
                        call_tool(
                            brain, params.get("name", ""), params.get("arguments") or {}
                        ),
                        False,
                    )
                except SystemExit as e:
                    text, is_error = str(e), True
                result = {
                    "content": [{"type": "text", "text": text}],
                    "isError": is_error,
                }
            else:
                raise LookupError(method)
            reply = {"jsonrpc": "2.0", "id": mid, "result": result}
        except LookupError as e:
            reply = {
                "jsonrpc": "2.0",
                "id": mid,
                "error": {"code": -32601, "message": f"method not found: {e}"},
            }
        except Exception as e:  # report, keep serving
            reply = {
                "jsonrpc": "2.0",
                "id": mid,
                "error": {"code": -32603, "message": str(e)},
            }
        sys.stdout.write(json.dumps(reply) + "\n")
        sys.stdout.flush()


# ---------- CLI ----------


def read_body(value: str | None) -> str:
    if value == "-" or value is None and not sys.stdin.isatty():
        return sys.stdin.read()
    return value or ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="brain", description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--dir", help="brain folder (default $AGENT_BRAIN_DIR or ~/.agent-brain)"
    )
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("recall", help="search active facts")
    r.add_argument("query", nargs="+")
    r.add_argument("-k", type=int, default=5)
    r.add_argument(
        "--all", action="store_true", help="include corrected and withdrawn pages"
    )
    r.add_argument("--json", action="store_true")

    m = sub.add_parser("remember", help="save one fact")
    m.add_argument("name")
    m.add_argument("-d", "--description", required=True)
    m.add_argument("-b", "--body", help="text, or - for stdin")
    m.add_argument("-t", "--type", default="reference", choices=TYPES)
    m.add_argument("-s", "--source", required=True, help="where this fact came from")
    m.add_argument(
        "--public",
        action="store_true",
        help="mark shareable (exported by `brain export`)",
    )

    c = sub.add_parser(
        "correct", help="replace a wrong fact, keep the old one as history"
    )
    c.add_argument("old")
    c.add_argument("name")
    c.add_argument("-d", "--description", required=True)
    c.add_argument("-b", "--body", help="text, or - for stdin")
    c.add_argument("-s", "--source", default="")

    f = sub.add_parser("forget", help="withdraw a fact")
    f.add_argument("name")
    f.add_argument("-r", "--reason", required=True)

    sub.add_parser("index", help="rebuild INDEX.md")
    sub.add_parser("lint", help="check frontmatter, links, secrets and dashes")
    e = sub.add_parser("export", help="copy public active pages to a folder")
    e.add_argument("dest")
    sub.add_parser("mcp", help="run the stdio MCP server")
    sub.add_parser("where", help="print the brain folder")

    a = ap.parse_args(argv)
    root = Path(
        a.dir or os.environ.get("AGENT_BRAIN_DIR") or Path.home() / ".agent-brain"
    ).expanduser()
    brain = Brain(root)

    if a.cmd == "recall":
        hits = brain.recall(" ".join(a.query), a.k, a.all)
        if a.json:
            print(json.dumps(hits, indent=1))
        elif not hits:
            print("no match")
        for h in [] if a.json else hits:
            flag = "" if h["status"] == "active" else f" [{h['status']}]"
            print(f"{h['score']:>6}  {h['name']}{flag} - {h['description']}")
    elif a.cmd == "remember":
        p = brain.remember(
            a.name,
            a.description,
            read_body(a.body),
            a.type,
            a.source,
            "public" if a.public else "private",
        )
        print(f"saved {p.path}")
    elif a.cmd == "correct":
        p = brain.correct(a.old, a.name, a.description, read_body(a.body), a.source)
        print(f"saved {p.path}; {a.old} marked corrected")
    elif a.cmd == "forget":
        print(f"withdrew {brain.forget(a.name, a.reason).slug}")
    elif a.cmd == "index":
        print(f"wrote {brain.index()}")
    elif a.cmd == "lint":
        errors = brain.lint()
        for err in errors:
            print(err)
        print(f"{len(brain.pages())} pages, {len(errors)} problems")
        return 1 if errors else 0
    elif a.cmd == "export":
        print(
            f"exported {brain.export(Path(a.dest).expanduser())} public pages to {a.dest}"
        )
    elif a.cmd == "mcp":
        serve_mcp(brain)
    elif a.cmd == "where":
        print(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
