---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/requirements*.txt"
---

# Python code rules

- Type hints always. Prefer `from __future__ import annotations` for Python 3.10+.
- f-strings, not `.format()` or `%`.
- `pathlib.Path`, not `os.path`.
- Package manager: `uv` preferred, else `pip --break-system-packages`.
- Tests: `pytest` with AAA pattern, one behavior per test.
- Never use `except:` bare. Catch specific exceptions.
