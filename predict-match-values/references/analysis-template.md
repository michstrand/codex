# Match Prediction Template

Use this reference when processing an unfinished match into `predictions`.

## Inputs

For each source row, capture:

- `id`
- `sport_key`
- `sport_title`
- `commence_time`
- `home_team`
- `away_team`
- Best odds and bookmakers for outcomes `1`, `X`, `2`
- Any relevant context gathered from the workbook or web
- The matching `latest_standings` league snapshot, including its embedded generation time or file modification time
- Current table, expected-performance metrics, prior-season baseline when present, and relevant injuries or suspensions for both teams
- Previous prediction rows with kickoff times earlier than the current match
- The complete current policy files from `betting_agent_directions`

## Market Calibration

- Normalize the three market implied probabilities after removing overround.
- Produce a raw `1/X/2` probability triplet summing to 100%.
- Assign evidence quality and uncertainty flags before selecting a reliability weight.
- Shrink every raw probability toward its market prior and calculate EV only from the calibrated triplet.
- Run the required second shrinkage pass for unusually large raw edges.
- Red-team every prospective bet and normally choose no more than one outcome.

## Local Standings Evidence

- Match both teams conservatively to unique club rows across the applicable files.
- Compare points, goal difference, xG difference, and xPTS on a per-match basis when matches played differ.
- Parse the leading expected totals from `xG`, `xGC`, and `xPTS`; recompute actual-minus-expected differences from the conventional table rather than trusting stored suffix signs.
- Use current results and expected metrics as complementary signals; do not count the same advantage twice.
- Use prior-season metrics as a baseline, especially early in a new season, but allow current-season evidence to take over as the sample grows.
- Ignore current-season ranks and rates when `MP` is zero; strongly shrink one- or two-match samples.
- Summarize only material absences. Treat null return dates and ambiguous, reserve-team, or cross-league club matches as uncertainty requiring verification.
- Exclude a current-season snapshot created after the kickoff when analyzing historical fixtures. Treat prior-season `generated_at` as extraction time, not the season's data cutoff.

## Historical Calibration

Before writing the new recommendation:

- Find comparable prior rows by league, team, outcome, implied-probability band, and market shape.
- Summarize the strongest relevant precedent compactly; do not list the entire history.
- Compare the proposed true probability and stake with those precedents.
- If settled results are available through a reliable match-ID join, use aggregate calibration rather than a single win or loss.
- Exclude future, current-match, duplicate, and unsettled outcomes from performance calculations.
- Treat sparse or conflicting history as a reason for caution, not as evidence for a bet.

## Context Summary

Write one concise paragraph covering the decisive factors only:

- market position and favorite/underdog shape
- recent form or league context
- current table position plus the most decision-relevant expected-performance or prior-season signal from `latest_standings`
- injuries, suspensions, schedule congestion, home/away splits, or motivation when known
- uncertainty that limits confidence

Avoid long previews. This field should support the recommendation, not become a full article.

## Outcome Rows

Create one row per outcome:

- `1`: home win
- `X`: draw
- `2`: away win

For each outcome:

- `market odds.outcome`: `1`, `X`, or `2`
- `market.odds.best.odds `: decimal odds
- `market odds.bookmaker`: bookmaker name
- `market odds.implied probability`: percentage with one decimal when useful, such as `44.2%`
- `recommendation`: include estimated true probability and EV edge
- `recommendation`: include normalized market prior, raw probability, reliability weight, calibrated probability, calibrated EV, red-team objection, and how prior recommendations affected confidence
- `final verdict`: `BET` or `NO BET`; if betting, include stake as `% bankroll` plus pre-kickoff invalidation conditions

## EV Language

Apply the action gates in the current `betting_agent_directions` files. Do not preserve an older threshold from this reference when the live policy changes. When model confidence is low, increase shrinkage and reduce or eliminate the stake even if raw arithmetic EV is positive.

