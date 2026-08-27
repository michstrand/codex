# Betting Directions Integration

Read this reference after reading the live files in the workspace `betting_agent_directions` folder. The live files are authoritative and must be reread before each prediction run.

## Current Direction Source

The inspected source on 2026-08-27 is `AI_Prediction_Agent_ROI_Improvement_Instructions.docx`. It contains paragraphs and three tables covering historical ROI diagnosis, calibrated-EV action gates, staking, red-team checks, output requirements, and continuous learning.

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
9. Normally select no more than one outcome; `NO BET` is a valid successful result.
10. State pre-kickoff invalidation conditions for any bet.

## Mapping Into Predictions A:M

Keep exactly three outcome rows. Encode the direction document's required information without changing the target schema:

- `Context summary`: quantitative team-strength basis, evidence grade, material uncertainty flags, and the strongest current contextual evidence.
- `market odds.implied probability`: the outcome's displayed raw implied percentage from its decimal odds; include the normalized market prior in `recommendation` so overround removal remains auditable.
- `recommendation`: normalized market prior, raw model probability, reliability weight, calibrated probability, calibrated EV, and the red-team objection. State when a second shrinkage pass was triggered.
- `final verdict`: `BET` or `NO BET`; for a bet, include stake as `% bankroll` and the specific conditions that would invalidate it before kickoff.

The three rows must use mutually coherent probability triplets. Do not calculate each outcome independently in a way that makes the raw or calibrated probabilities fail to sum to approximately 100%.

## Historical Calibration

Use settled prediction history as temporary calibration evidence, not a permanent league ranking. Recompute current diagnostics from the workbook when feasible rather than copying historical values from the direction document indefinitely.

Track performance by calibrated-EV band, odds band, league, outcome type, favorite/underdog status, and evidence grade. Prefer out-of-sample or rolling evidence. Do not materially change policy from fewer than 30 settled bets in a diagnostic group; require about 100 before a strong structural change unless the live directions specify otherwise.

