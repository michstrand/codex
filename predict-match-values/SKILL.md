---
name: predict-match-values
description: Process unfinished football matches in a Google Sheets matches workbook by league tab, analyze each 1X2 outcome for positive expected value, insert one prediction row per outcome into the predictions tab, and mark the source match row done. Use when the user asks to predict matches, fill the predictions tab, process rows where done is not TRUE, or run value-betting analysis for Denmark, England, France, Germany, Spain, or Italy match tabs.
---

# Predict Match Values

Use this skill to process match rows from the `matches` Google Sheet into the `predictions` tab.

The source match tabs are expected to follow this schema:

`id`, `sport_key`, `sport_title`, `commence_time`, `home_team`, `away_team`, `bookmakers`, `done`, `result`, `home_goals`, `away_goals`, `best_odds_1`, `bookmaker_1`, `best_odds_X`, `bookmaker_X`, `best_odds_2`, `bookmaker_2`, `odds_found`.

The target `predictions` tab is expected to use columns `A:M`:

`id`, `sport_key`, `sport_title`, `commence_time`, `home_team`, `away_team`, `Context summary`, `market odds.outcome`, `market.odds.best.odds `, `market odds.bookmaker`, `market odds.implied probability`, `recommendation`, `final verdict`.

## Workflow

1. Use the Google Sheets/Drive connector. Read the Google Sheets skill instructions before live reads or writes.
2. Resolve the spreadsheet ID. If the user says `matches`, search Drive for the spreadsheet before asking.
3. Read spreadsheet metadata and confirm the `predictions` tab plus requested league source tabs exist.
4. Select league tabs from user input:
   - Danish / Denmark / Superliga -> `soccer_denmark_superliga`
   - English / England / EPL / Premier League -> `soccer_epl`
   - French / France / Ligue 1 -> `soccer_france_ligue_one`
   - German / Germany / Bundesliga -> `soccer_germany_bundesliga`
   - Spanish / Spain / La Liga -> `soccer_spain_la_liga`
   - Italian / Italy / Serie A -> `soccer_italy_serie_a`
5. Read each selected source tab header and rows within existing sheet bounds. Process only rows where `done` is not `TRUE`; treat blank, `FALSE`, and any other value as unfinished.
6. For each unfinished match, use available row data first:
   - Best 1X2 odds and bookmakers from columns `L:Q`.
   - Bookmaker JSON in column `G` if the best-odds columns are missing or stale.
   - Existing contextual columns if present in the workbook.
7. Retrieve missing contextual data with web search when needed. Prefer primary or reputable sources for team news, form, injuries, standings, schedules, and head-to-head context. Cite sources in the conversation if presenting the analysis to the user.
8. Produce exactly three prediction rows per match, one for each outcome `1`, `X`, and `2`.
9. Insert prediction rows into the first empty row of the `predictions` tab. Use `scripts/build_prediction_requests.py` to generate the `updateCells` request when convenient.
10. Verify the inserted prediction rows by reading them back from the `predictions` tab.
11. Only after successful verification, update the source match tab `done` column (`H`) to boolean `TRUE` for the processed source row.
12. Verify the source `done` cells after writing.

## Prediction Standards

Use the same compact value-betting style as prior analyses:

- Compute implied probability as `1 / decimal_odds`.
- Estimate a true probability for each outcome using market odds plus contextual evidence.
- Compute EV edge as `(estimated_probability * decimal_odds) - 1`.
- Use cautious staking language. Recommend a bet only when the estimated edge is meaningful enough for the available uncertainty.
- If the edge is thin or evidence is weak, say `No bet`, `Lean only`, or `Avoid`.

Read `references/analysis-template.md` before generating predictions if the prompt asks for detailed rationale or if many matches are being processed.

## Batch Safety

For multi-match runs:

- Process in small batches that can be verified, especially when web research is required.
- Keep a local note of source tab name, source row number, and inserted prediction row range until verification is complete.
- Do not mark `done` for a match whose prediction rows failed to insert or cannot be verified.
- If a row has no usable 1X2 odds, leave `done` unchanged and report it as skipped.

## Helper Script

Use `scripts/build_prediction_requests.py` to convert structured predictions to Google Sheets `batchUpdate` requests.

Example:

```powershell
python scripts/build_prediction_requests.py --input predictions_payload.json
```

The script prints JSON containing:

- `prediction_requests`: requests to insert/update rows in `predictions`.
- `done_requests`: requests to mark source rows done after verification.

Apply `prediction_requests` first, verify, then apply `done_requests`.
