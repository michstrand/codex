# One-Time No-Touch Setup

Run this once from a visible Windows PowerShell terminal:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\micha\.codex\skills\refresh-betting-dashboard\scripts\setup_no_touch.ps1"
```

The setup asks for the Synology login password while installing a dedicated public key, then asks for the sudo password while installing one exact `NOPASSWD` Docker Compose command. Passwords remain in the terminal and are not stored by the skill.

The resulting unattended scope is limited to:

```text
/usr/local/bin/docker compose -f /volume1/docker/edge-dashboard/docker-compose.yml up -d --build
```

The deploy script uses `BatchMode=yes`, so a missing key or sudo rule fails immediately instead of hanging at a prompt.
