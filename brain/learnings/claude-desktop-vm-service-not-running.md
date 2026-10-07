---
name: claude-desktop-vm-service-not-running
description: "Claude Desktop on Windows showing VM service not running means the CoworkVMService Windows service is stopped; start it, because restart and reinstall never touch it"
type: reference
source: "observed 2026-07-05 and 2026-07-13 on Claude Desktop (MSIX install) on Windows 11, recurring after app updates"
created: 2026-07-05
modified: 2026-10-07
status: active
visibility: public
---

Error: "Failed to start Claude's workspace / VM service not running. The service failed to start."

**Root cause:** the Windows service `CoworkVMService` (binary `cowork-svc.exe` inside the Claude MSIX package under `C:\Program Files\WindowsApps\Claude_*\app\resources\`) is STOPPED. The app talks to it over the named pipe `\\.\pipe\cowork-vm-service`; with the service down the pipe is missing (`connect ENOENT`) and every `startVM` call fails.

**Fix:** `Start-Service CoworkVMService` (PowerShell) or `sc start CoworkVMService`. It reaches RUNNING in about 3 seconds. It worked from a normal shell in one case (the service ACL allows a user start); use an elevated terminal if you get access denied.

**Why restart and reinstall do not help:** "Reinstall workspace" only deletes and re-extracts the VM bundle (rootfs, initrd, kernel under the app's `vm_bundles` directory). It never touches the Windows service, and neither does restarting the app. The service is set to auto start but gets stopped by MSIX servicing during app updates (SCM event 7040 showed the start type flipping from auto to disabled right after an update), crashes, or fast startup, and nothing restarts it until a reboot.

**Diagnostics:**

- `Get-Service CoworkVMService` or `sc query CoworkVMService` confirms STOPPED.
- The app logs (under `%LOCALAPPDATA%\Claude-3p\logs\` for the third-party-provider install) show ENOENT pipe spam in `cowork_vm_node.log` and `[ScheduledTasks] startVM failed` in `main.log`.

Related: [[claude-desktop-bedrock-config-gotchas]].
