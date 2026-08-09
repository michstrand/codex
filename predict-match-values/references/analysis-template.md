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

## Context Summary

Write one concise paragraph covering the decisive factors only:

- market position and favorite/underdog shape
- recent form or league context
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
- `final verdict`: short action, such as `0 units`, `Lean only`, or `0.25 units`

## EV Language

Use this scale:

- Negative EV: `Avoid` or `No bet`
- 0% to +2% edge: `No bet` or `Lean only`; usually no stake
- +2% to +5% edge: `Small positive EV`; usually 0.25 to 0.5 units
- Above +5% edge: `Positive EV`; consider a stronger recommendation only if context supports it

When model confidence is low, reduce staking even if the arithmetic edge is positive.
