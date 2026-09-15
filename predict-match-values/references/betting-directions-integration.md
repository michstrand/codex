# Betting Directions Integration

Read this reference after reading the live files in the workspace `betting_agent_directions` folder. The live files are authoritative and must be reread before each prediction run.

## Current Direction Source

The current source is `AI_Prediction_Agent_ROI_Improvement_Instructions.docx`. It contains the live probability, calibrated-EV, staking, measurement, and auditability policy. Inspect its current version and effective date on every run.

Do not assume this remains the only file or that its numbers remain unchanged. Enumerate the folder recursively and read the complete current content every run.

## Decision Sequence

For each match:

1. Convert best 1X2 odds to implied probabilities and normalize them to sum to 100%.
2. Build raw probabilities for all three outcomes from independent quantitative evidence; make them sum to 100%.
3. Grade evidence quality and list uncertainty flags.
4. Select a reliability weight from the live directions and shrink raw probabilities toward the normalized market prior.
5. Re-normalize calibrated probabilities if rounding creates a material departure from 100%.
6. Calculate calibrated EV for all outcomes.
7. Red-team every outcome that could qualify as a bet.
8. Apply the live EV, odds, evidence, league, and staking gates.
9. Normally select no more than one outcome as either `BET` or `SHADOW BET`; `NO BET` is a valid successful result. Apply [shadow-bet-mode.md](shadow-bet-mode.md) only after the real-money decision.
10. State pre-kickoff invalidation conditions for any bet.

## Mapping Into Predictions A:AD

Keep exactly three outcome rows. Encode the direction document's required information without changing the target schema:

- `Context summary`: quantitative team-strength basis, evidence grade, material uncertainty flags, and the strongest current contextual evidence.
- `market odds.implied probability`: the outcome's displayed raw implied percentage from its decimal odds; include the normalized market prior in `recommendation` so overround removal remains auditable.
- `recommendation`: normalized market prior, raw model probability, reliability weight, calibrated probability, calibrated EV, and the red-team objection. State when a second shrinkage pass was triggered.
- `final verdict`: `BET`, `SHADOW BET`, or `NO BET`. For a real bet, include stake as `% bankroll` and the specific conditions that would invalidate it before kickoff. For a shadow bet, state `hypothetical 0.25% bankroll; not placed` and the same invalidation conditions.
- `recommended stake pct`: numeric bankroll percentage for the outcome. Use the selected real stake for a `BET` and numeric `0` for every other outcome, including `SHADOW BET`. Populate this field on all three rows.
- `EV edge %`: calibrated EV in percentage points, not decimal form. For example, write `5.4` when `(calibrated_probability × odds) − 1 = 0.054`. Populate this field on all three rows, including zero and negative values.
- `prediction timestamp`, `policy version`, `model version`, `odds timestamp`, and `evidence snapshot date`: populate these audit fields on every new row. Use the policy version stated in the live direction file.
- `bet placed`: write boolean `FALSE` when the recommendation is created. Change it to `TRUE` only when placement is confirmed, then record `actual stake pct`, `actual stake amount`, `actual odds`, and `placement timestamp`.

Leave settlement fields `result`, `home_team_score`, and `away_team_score` blank when the match has not yet settled. Leave actual-placement fields blank until placement is confirmed. Columns `actual return` and `is win` are calculated by the sheet and must not be written by the prediction workflow.

The three rows must use mutually coherent probability triplets. Do not calculate each outcome independently in a way that makes the raw or calibrated probabilities fail to sum to approximately 100%.

## Historical Calibration

Use settled prediction history as temporary calibration evidence, not a permanent league ranking. Recompute current diagnostics from the workbook when feasible rather than copying historical values from the direction document indefinitely.

Track performance by calibrated-EV band, odds band, league, outcome type, favorite/underdog status, and evidence grade. Prefer out-of-sample or rolling evidence. Do not materially change policy from fewer than 30 settled bets in a diagnostic group; require about 100 before a strong structural change unless the live directions specify otherwise.

For every settled match, compare multiclass Brier score for the calibrated model with the normalized market on the same match. Count the match once. Keep recommendation performance separate from confirmed-wager ROI, and split both by policy and model version.

Track shadow bets as a separate prospective cohort. Report count, wins, flat-stake return, hypothetical return at 0.25% per selection, odds distribution, evidence grades, and model-versus-market Brier score. Never include them in confirmed-wager ROI.
