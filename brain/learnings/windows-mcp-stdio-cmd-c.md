---
name: windows-mcp-stdio-cmd-c
description: "On native Windows, launch npx-based stdio MCP servers through cmd /c npx, not bare npx"
type: reference
source: "observed configuring stdio MCP servers for Claude Code on Windows 11, last confirmed 2026-07-26"
created: 2026-07-26
modified: 2026-10-07
status: active
visibility: public
---

On native Windows, a stdio MCP server configured as `"command": "npx"` fails to start, because `npx` there is a `.cmd` batch shim that cannot be spawned directly without a shell. Wrap it in `cmd /c`:

```json
{
  "mcpServers": {
    "example": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "<package>"]
    }
  }
}
```

**How to apply:** when a Windows stdio server shows as failed to connect, check the launcher first. Put MCP server configs in `.mcp.json` (project) or the user-level MCP config, not in the general settings file.

Related: [[windows-bash-gotchas]].
