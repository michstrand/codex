# Normalized Input Contract

`build_dashboard_json.py` accepts either a root array or an object with a `picks` array. Each pick requires:

```json
{
  "id": "match identifier",
  "sport_key": "soccer_epl",
  "sport_title": "Premier League",
  "commence_time": "2026-09-12T14:00:00Z",
  "home_team": "Crystal Palace",
  "away_team": "Ipswich Town",
  "outcome": "X",
  "odds": 3.94,
  "bookmaker": "1xBet",
  "true_probability": 0.2801,
  "ev": 0.1036,
  "stake_pct": 1.5
}
```

Optional fields are `home_code`, `away_code`, `competition`, `country`, and `flag`. Supply them when the spreadsheet has authoritative display values. The builder otherwise derives them.

Normalize spreadsheet headers semantically. Typical equivalents are:

- `outcome`: `outcome`, `market odds.outcome`, or selection (`1`, `X`, `2`)
- `odds`: `odds`, `market.odds.best.odds `, or selected best odds
- `bookmaker`: `bookmaker` or `market odds.bookmaker`
- `true_probability`: `trueP`, calibrated probability, or confidence as a fraction/percentage
- `ev`: `EV`, `EV edge %`, or edge as a fraction/percentage
- `stake_pct`: `stake`, `Betting pct`, or bankroll percentage

Do not substitute raw implied probability for `true_probability`. If a required field is absent or ambiguous, stop instead of estimating it.
