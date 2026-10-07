---
name: python-tooling-gotchas
description: "importlib returns None for non-.py paths, and a .venv pointing at a removed Python breaks until recreated with uv"
type: reference
source: "observed 2026-09-23 and 2026-10-06 in uv-managed Python projects on Windows"
created: 2026-09-23
modified: 2026-10-07
status: active
visibility: public
---

- **`importlib.util.spec_from_file_location` returns `None` for a non-`.py` path** such as `x.py.bak-20260923`. Use `importlib.machinery.SourceFileLoader(name, path)` with `importlib.util.spec_from_loader(name, loader)` instead.
- **Old virtualenvs break after a Python cleanup.** A `.venv` pointing at an uninstalled interpreter fails with "No Python at ...". Fix: `uv venv --clear --python <version>` then `uv sync`.

Related: [[dependency-sweep-gotchas]].
