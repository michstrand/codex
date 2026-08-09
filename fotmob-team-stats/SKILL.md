---
name: fotmob-team-stats
description: Extract FotMob league team statistics pages into structured JSON. Use when the user asks to parse, scrape, re-run, or export a FotMob `/leagues/<id>/stats/.../teams` page, such as Superligaen team stats, and wants a local JSON file with page metadata, league/season info, stat categories, top teams, and full team rankings.
---

# FotMob Team Stats

## Overview

Use this skill to turn a FotMob league team statistics page into a local JSON artifact. The bundled PowerShell script reads the page's Next.js `__NEXT_DATA__`, follows each `fetchAllUrl` for the complete rankings, and writes one structured JSON file.

## Quick Start

Run the bundled script from the skill folder:

```powershell
.\scripts\export_fotmob_team_stats.ps1 `
  -Url "https://www.fotmob.com/da/leagues/46/stats/superligaen/teams" `
  -OutFile "C:\CHAT-GPT\my-first-project\fotmob_superligaen_team_stats.json"
```

If network access is blocked in the sandbox, rerun the same command with `require_escalated` and a concise justification asking permission to fetch the FotMob page and linked JSON stat endpoints. A good reusable approval prefix is `["powershell", "-ExecutionPolicy", "Bypass", "-File"]` only when invoking this script exactly via `-File`.

## Workflow

1. Confirm the input URL is a FotMob team stats page ending in `/teams`.
2. Choose an output path in the user's workspace unless they specify another location.
3. Execute `scripts/export_fotmob_team_stats.ps1`.
4. Validate the output with `ConvertFrom-Json` or a short script:
   - `league.name` and `league.selected_season` are populated.
   - `team_statistics` has entries.
   - Each stat has `full_ranking.rows`.
5. Report the output path and a short summary: league, season, number of stat categories, and whether full rankings were fetched.

## Output Shape

The JSON file contains:

- `source`: source URL, extraction timestamp, Next.js page/build metadata.
- `league`: league id, name, country, selected season, latest season, data provider.
- `season_stat_links`: FotMob's available season stat links from the page.
- `team_statistics`: one entry per team stat category.

Each `team_statistics[]` entry contains:

- `name`, `header`, `category`, `localized_title_id`, `order`.
- `fetch_all_url`: FotMob data endpoint used for the full ranking.
- `leader`: page leader.
- `top_three_from_page`: top teams embedded in the original page.
- `full_ranking.rows`: full ranked team list for that stat.

## Notes

- Prefer the bundled PowerShell script on Windows. In this Codex desktop environment, Python HTTPS may fail with an OpenSSL Applink error.
- Do not invent FotMob endpoints. Use the `fetchAllUrl` values embedded in the page.
- FotMob data is current/live and can change. Always refetch when the user asks for current or latest data.
