---
name: find-best-odds
description: Update Google Sheets match tabs with best 1X2 football odds from bookmaker JSON. Use when the user asks to fill or refresh best_odds_1/bookmaker_1, best_odds_X/bookmaker_X, best_odds_2/bookmaker_2, or odds_found columns for one league tab, several league tabs, or all matching league tabs in a Google Sheet such as a matches workbook.
---

# Find Best Odds

Use this skill to update existing Google Sheets match tabs whose rows follow this schema:

`home_team` in column `E`, `away_team` in column `F`, bookmaker JSON in column `G`, and target output columns `L:R`:

`best_odds_1`, `bookmaker_1`, `best_odds_X`, `bookmaker_X`, `best_odds_2`, `bookmaker_2`, `odds_found`.

## Workflow

1. Use the Google Sheets/Drive connector. Read its Google Sheets skill instructions before live reads or writes.
2. Resolve the spreadsheet ID. If the user says `matches`, search Drive for the spreadsheet before asking.
3. Read spreadsheet metadata and record tab names, `sheetId`, row counts, and column counts.
4. Select tabs:
   - `all`: every tab whose header row has the required `A:R` schema.
   - one league: the exact tab named by the user, such as `soccer_epl`.
   - multiple leagues: the named tabs only.
5. Read each candidate tab header `A1:R1`. Skip tabs whose headers do not match the expected schema unless the user explicitly asks to adapt them.
6. Before writing, inspect target cells `L2:R3` with `get_spreadsheet_cells` if validation or formulas may matter.
7. Generate a Google Sheets `batchUpdate` request with `scripts/build_best_odds_requests.py`.
8. Apply the generated structured requests using `_batch_update_spreadsheet`.
9. Verify results by reading `L2:R4` from each updated tab as formatted values, and read `L2:R3` from at least one tab with `value_render_option="FORMULA"`.

## Formula Behavior

The formulas parse the bookmaker JSON in `G` per row and only use the normal `h2h` outcome block. They intentionally avoid Betfair `h2h_lay` prices by splitting each bookmaker block at `","title":"` and extracting the first matching `name/price` pair from each bookmaker segment.

Prices in JSON use dot decimals. The formulas convert them to the spreadsheet locale by replacing `.` with `,` before `VALUE`.

`odds_found` is `TRUE` only when all three best odds are present.

## User Input Patterns

Examples:

- "Use `$find-best-odds` for all tabs in matches."
- "Run `$find-best-odds` for soccer_epl."
- "Update best odds for soccer_epl, soccer_spain_la_liga and soccer_italy_serie_a."

If the user gives common league names, map them conservatively:

- EPL / English / Premier League -> `soccer_epl`
- German / Bundesliga -> `soccer_germany_bundesliga`
- French / Ligue 1 -> `soccer_france_ligue_one`
- Spanish / La Liga -> `soccer_spain_la_liga`
- Italian / Serie A -> `soccer_italy_serie_a`
- Danish / Superliga -> `soccer_denmark_superliga`

## Script

Use `scripts/build_best_odds_requests.py` to avoid hand-writing long formula requests.

Example:

```powershell
python scripts/build_best_odds_requests.py --tabs soccer_epl:1279678532:615 soccer_spain_la_liga:908092425:652
```

The script prints JSON:

```json
{
  "requests": [
    { "copyPaste": { "...": "..." } }
  ]
}
```

Pass the `requests` array directly to `_batch_update_spreadsheet`.

Read `references/formulas.md` only when you need to inspect or modify the exact formula template.
