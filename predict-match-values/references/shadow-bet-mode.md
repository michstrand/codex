# Shadow Bet Mode

Read this reference before assigning the final decision for a match.

## Purpose

A shadow bet is a prospective model selection used to measure a plausible candidate without recommending or recording a real wager. It addresses low selection volume while preserving the live policy's real-money protections.

## Decision Order

1. Apply the live policy and decide whether any outcome qualifies as a real `BET`.
2. If a real bet qualifies, select it and do not create a shadow bet for that match.
3. If no real bet qualifies, test all three outcomes against the shadow criteria below.
4. If more than one qualifies, select only the outcome with the highest calibrated EV.
5. If none qualifies, use `NO BET` for all three outcomes.

## Eligibility

An outcome qualifies as `SHADOW BET` only when all conditions hold:

- calibrated EV is at least 2.0% and no more than 10.0%
- decimal odds are below 4.00
- evidence grade is exactly `Medium` or `High`; `Medium-Low`, `Low-to-moderate`, and `Low` do not qualify
- the probability and EV were produced after all required market shrinkage and any mandatory second pass
- the red-team review finds no unresolved material lineup, source-timing, promoted-team, model-input, or data-quality defect
- the candidate does not depend mainly on narrative reasoning, isolated head-to-head results, or correlated signals presented as independent confirmation

Do not lower these thresholds to reach a desired number of shadow bets.

## Sheet Encoding

For the selected outcome:

- start `final verdict` with `SHADOW BET`
- state the outcome, odds, `hypothetical 0.25% bankroll; not placed`, and pre-kickoff invalidation conditions
- include `shadow stake 0.25%` in `recommendation`
- write numeric `0` to `recommended stake pct`
- write boolean `FALSE` to `bet placed`
- leave `actual stake pct`, `actual stake amount`, `actual odds`, and `placement timestamp` blank

For the other two outcomes, use `NO BET`, recommended stake `0`, and bet placed `FALSE`.

## Evaluation And Promotion

After settlement, track shadow bets separately from real recommendations and confirmed wagers. Report:

- number of selections and wins
- flat-stake return and hypothetical return using 0.25% bankroll per selection
- results by odds band, league, and outcome type
- evidence-grade distribution
- calibrated model Brier score compared with normalized market probability on the same matches

Do not promote the shadow rule to real-money eligibility before at least 30 settled shadow bets. At that point, promotion may be considered only when the cohort has positive flat-stake return, its calibrated probabilities do not underperform the market Brier score, and results are not dominated by one league, outcome type, or a few high-odds wins. Promotion requires an explicit policy update; the skill must never promote the rule automatically.
