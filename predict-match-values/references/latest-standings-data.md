# Latest Standings Data

Read this reference before using the workspace `latest_standings` folder for a prediction.

## Actual File Shapes

Each league folder can contain:

- `standings.json`: object with `field_definitions` and `rows`. Rows contain `Rank`, `Team`, `MP`, `W`, `D`, `L`, `GS`, `GC`, and `PT`.
- `table-of-justice.json`: object with `field_definitions` and `rows`. Rows contain `Rank`, `Team`, `MP`, `xG`, `xGC`, `xGOT`, `xGFH`, `xGSH`, `xGOP`, `xGSP`, and `xPTS`.
- `standings_2025.json`: object with metadata and `standings`. Rows contain `team`, `W`, `D`, `L`, `G`, `GA`, `PTS`, `xG`, `NPxG`, `xGA`, `NPxGA`, `NPxGD`, `PPDA`, `OPPDA`, `DC`, `ODC`, and `xPTS`. Infer matches played as `W + D + L`.
- `injuries.json`: array of `player`, `club`, `injury`, `since`, and `estimated_return` records plus source URLs.
- `suspensions.json`: empty array, array, or a bare record object with `player`, `club`, `reason`, `until`, and `matches` plus source URLs. Normalize a bare object to a one-item list.

Use keys and containers detected in the file, not the filename alone. Skip a malformed record without discarding other valid sources for the match.

## Coverage Observed on 2026-08-27

- All six league folders have current `standings.json`, `table-of-justice.json`, injuries, and suspensions files.
- `standings_2025.json` exists for Bundesliga, Premier League, Ligue 1, La Liga, and Serie A. It is absent for the Danish Superliga.
- Bundesliga current standings and expected-performance rows have `MP = 0`; they provide no current-season performance evidence until populated.
- The other current-season tables are very early samples: Denmark has four or five matches per team, La Liga one or two, and the Premier League, Ligue 1, and Serie A one.

Reinspect the folder on each run because these files are refreshed and coverage can change.

## Expected-Metric Parsing

In `table-of-justice.json`, `xG`, `xGC`, and `xPTS` are strings containing a leading expected total plus a signed suffix. Parse the first numeric token as the expected total.

Do not use the supplied suffix as an over/under-performance signal. The field definition says it is `actual − expected`, but observed rows use the opposite sign. Recompute from the conventional table after a reliable team join:

- finishing difference = `GS − xG`
- concession difference = `GC − xGC`
- points difference = `PT − xPTS`
- underlying goal difference per match = `(xG − xGC) / MP`

When the table join is unavailable, use the expected totals or per-match rates but omit the signed variance claim.

## Team Joining

Use the current `standings.json` team list as the league membership reference. Normalize Unicode accents, case, punctuation, spacing, and common legal or football suffixes. Resolve common abbreviations semantically, such as Manchester/Man, Borussia Dortmund/Borussia D., Paris Saint-Germain/PSG, AC Milan/Milan, FC Copenhagen/Copenhagen, and Venezia/Venice.

Require one unique current-league match. Do not use an absence or prior-season row when normalization yields zero or multiple candidates. Prior-season files legitimately contain relegated teams and omit promoted teams; absence sources can also contain reserve or wrong-league clubs.

Known contamination examples found during inspection:

- Bundesliga suspensions contains `Eintracht Frankfurt II`, a reserve side.
- Ligue 1 suspensions contains a `Sunderland AFC` row.

These examples are not an exhaustive blocklist; enforce current-league membership generally.

## Availability Interpretation

- All currently inspected injury rows have `estimated_return: null`. Treat them as reported injuries of unknown return status.
- Dates use `DD/MM/YYYY` strings.
- A suspension `until` date and `matches` count describe the source listing, but do not prove the player will miss this exact fixture.
- Empty absence arrays mean no listed records from that snapshot, not verified full availability.

Verify high-impact players close to kickoff, and only include an absence in the prediction context when club identity and likely match relevance are credible.

## Weighting

- Market probabilities remain the baseline.
- At `MP = 0`, ignore current rank and current rates.
- At one or two matches, use current data only as a weak directional update and lean substantially on the market and prior season.
- At four or five matches, current evidence can carry more weight but still requires shrinkage.
- Use prior-season per-match metrics as a baseline, not a direct forecast; promoted clubs may have no row.
- Avoid counting results, goal difference, xPTS, and xG difference as independent full-strength signals when they describe the same small sample.

