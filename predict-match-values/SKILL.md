---
name: predict-match-values
description: Process unfinished football matches in a Google Sheets matches workbook by league tab, using local latest_standings league tables, expected-performance data, injuries, suspensions, prior prediction history, and market odds to analyze 1X2 value, write one row per outcome, and mark verified source rows done. Use when the user asks to predict matches, fill the predictions tab, process rows where done is not TRUE, or run value-betting analysis for Denmark, England, France, Germany, Spain, or Italy match tabs.
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
4. Read the populated range of the `predictions` tab before analyzing new matches. Build a compact history of prior recommendations using match ID, league, kickoff time, teams, outcome, odds, implied probability, recommendation, and final verdict. Use only rows with kickoff times earlier than the match being analyzed.
5. Select league tabs from user input:
   - Danish / Denmark / Superliga -> `soccer_denmark_superliga`
   - English / England / EPL / Premier League -> `soccer_epl`
   - French / France / Ligue 1 -> `soccer_france_ligue_one`
   - German / Germany / Bundesliga -> `soccer_germany_bundesliga`
   - Spanish / Spain / La Liga -> `soccer_spain_la_liga`
   - Italian / Italy / Serie A -> `soccer_italy_serie_a`
6. Locate the workspace folder named `latest_standings` and read the matching league subfolder before predicting. Use this mapping:
   - `soccer_denmark_superliga` -> `danish-superliga`
   - `soccer_epl` -> `premier-league`
   - `soccer_france_ligue_one` -> `ligue-1`
   - `soccer_germany_bundesliga` -> `bundesliga`
   - `soccer_spain_la_liga` -> `la-liga`
   - `soccer_italy_serie_a` -> `serie-a`
7. Read [references/latest-standings-data.md](references/latest-standings-data.md), then load and normalize the available JSON files. Do not assume identical top-level containers: tables use `rows`, prior-season data uses `standings`, injury files use arrays, and a suspension file with exactly one entry may be serialized as a bare object. Normalize every absence source to a list before filtering.
8. Normalize team names conservatively across the match row and local files: case-fold, remove accents and harmless punctuation, and allow well-known suffix variants such as `FC`, `CF`, or `IF`. Require a unique, credible match; do not attach another club's data after a fuzzy or reserve-team-only match. Record unmatched or ambiguous teams as uncertainty.
9. Read each selected source tab header and rows within existing sheet bounds. Process only rows where `done` is not `TRUE`; treat blank, `FALSE`, and any other value as unfinished.
10. For each unfinished match, use available row data first:
   - Best 1X2 odds and bookmakers from columns `L:Q`.
   - Bookmaker JSON in column `G` if the best-odds columns are missing or stale.
   - Existing contextual columns if present in the workbook.
11. Build a compact local evidence profile for both teams. Compare current rank and points per match, goal difference per match, expected goal difference per match, expected-points difference, last-season strength when available, and relevant confirmed/listed absences. Weight rates and differences more than raw totals when teams have played different numbers of matches. If `MP` is zero, do not derive rates or treat rank order as evidence.
12. Check temporal safety before relying on a file. For current-season snapshots without `generated_at`, use file modification time as the snapshot time; do not use them for a historical match that kicked off earlier. For `standings_2025.json`, `generated_at` is the extraction time, while `season_start_year` identifies the completed prior-season period; do not reject a legitimate prior-season baseline merely because it was exported later. Treat stale, incomplete, or temporally unsafe files as unavailable and lower confidence rather than silently using them.
13. Retrieve missing or fresher contextual data with web search when needed. Prefer primary or reputable sources for team news, form, injuries, standings, schedules, and head-to-head context. Local absence lists are leads, not guaranteed match-day status: verify material absences when their return date is missing, ambiguous, or close to kickoff. Cite sources in the conversation if presenting the analysis to the user.
14. Compare the new match with prior prediction rows before finalizing probabilities or stakes. Prefer same-league rows, recurring teams, similar favorite/underdog profiles, comparable implied-probability bands, and the same outcome. Treat history as calibration evidence, not as a substitute for current information.
15. Produce exactly three prediction rows per match, one for each outcome `1`, `X`, and `2`.
16. Insert prediction rows into the first empty row of the `predictions` tab. Use `scripts/build_prediction_requests.py` to generate the `updateCells` request when convenient.
17. Verify the inserted prediction rows by reading them back from the `predictions` tab.
18. Only after successful verification, update the source match tab `done` column (`H`) to boolean `TRUE` for the processed source row.
19. Verify the source `done` cells after writing.

## Prediction Standards

Use the same compact value-betting style as prior analyses:

- Compute implied probability as `1 / decimal_odds`.
- Estimate a true probability for each outcome using market odds plus contextual evidence.
- Use `latest_standings` as a structured adjustment to the market baseline, not as a standalone prediction model. Current-season performance should normally outweigh prior-season data; expected metrics help distinguish sustainable strength from finishing or results variance.
- Parse the leading expected value from strings such as `"7.0 -3.0"`. Do not trust the signed suffix or its supplied definition: observed files encode it inconsistently with the stated `actual − expected` definition. When actual totals are available, recompute over/under-performance directly, such as `actual GS − parsed xG`, `actual GC − parsed xGC`, and `actual PT − parsed xPTS`.
- Do not double-count the same signal across the conventional table and expected-performance table. For example, rank and points describe results, while xG, xGC, and xPTS describe underlying performance.
- Interpret short current-season samples cautiously. When matches played are low, shrink conclusions toward market probabilities and prior-season strength, and reduce stakes.
- Treat injuries and suspensions by likely team impact and timing, not by raw player count. Current injury files have null `estimated_return` values, so they establish a reported injury only—not confirmed match-day unavailability. Reject absence rows whose club cannot be matched uniquely to a current team in the selected league, including reserve teams or cross-league contamination.
- Compute EV edge as `(estimated_probability * decimal_odds) - 1`.
- Check whether the proposed probability, verdict, and stake are consistent with comparable previous recommendations. Explain material departures in the recommendation text.
- If settled results can be joined safely from source match tabs by match ID, use aggregate historical calibration and hit rate to moderate confidence. Never use a result from the current match or any match that had not finished before the current match's kickoff.
- Do not infer accuracy from unsettled recommendations. Do not copy a prior verdict solely because the teams or odds look similar.
- Reduce confidence or stake when comparable prior recommendations were overconfident, contradictory, or too sparse. Preserve the current evidence-based estimate when history is irrelevant.
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

