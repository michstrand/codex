#!/usr/bin/env python3
"""Build Google Sheets batchUpdate requests for match predictions.

Input JSON shape:
{
  "prediction_sheet_id": 684671255,
  "prediction_start_row": 8,
  "source_done_column": "H",
  "matches": [
    {
      "source_sheet_id": 0,
      "source_row": 3,
      "id": "...",
      "sport_key": "soccer_denmark_superliga",
      "sport_title": "Denmark Superliga",
      "commence_time": "2026-08-09T16:00:00Z",
      "home_team": "AC Horsens",
      "away_team": "Brondby IF",
      "context_summary": "...",
      "evidence_grade": "Medium",
      "prediction_timestamp": "2026-09-15T10:00:00Z",
      "policy_version": "1.1 (2026-09-15)",
      "model_version": "gpt-5",
      "odds_timestamp": "2026-09-15T09:55:00Z",
      "evidence_snapshot_date": "2026-09-15",
      "outcomes": [
        {
          "outcome": "1",
          "odds": 5.2,
          "bookmaker": "Betfair",
          "implied_probability": "19.2%",
          "recommendation": "No bet...",
          "final_verdict": "0 units...",
          "betting_pct": 0,
          "ev_edge_pct": -1.7
        }
      ]
    }
  ]
}
"""

from __future__ import annotations

import argparse
import json
import string
import sys
from pathlib import Path
from typing import Any


CORE_COLUMNS = 20  # A:T. U:V are calculated by the sheet.
AUDIT_START_COLUMN = 22  # W
AUDIT_COLUMNS = 8  # W:AD


def column_to_index(column: str) -> int:
    value = 0
    for char in column.strip().upper():
        if char not in string.ascii_uppercase:
            raise ValueError(f"Invalid column letter: {column!r}")
        value = value * 26 + (ord(char) - ord("A") + 1)
    return value - 1


def cell_value(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, bool):
        return {"userEnteredValue": {"boolValue": value}}
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return {"userEnteredValue": {"numberValue": float(value)}}
    return {"userEnteredValue": {"stringValue": str(value)}}


def prediction_core_row(match: dict[str, Any], outcome: dict[str, Any]) -> list[Any]:
    return [
        match.get("id", ""),
        match.get("sport_key", ""),
        match.get("sport_title", ""),
        match.get("commence_time", ""),
        match.get("home_team", ""),
        match.get("away_team", ""),
        match.get("context_summary", ""),
        outcome.get("outcome", ""),
        outcome.get("odds", ""),
        outcome.get("bookmaker", ""),
        outcome.get("implied_probability", ""),
        outcome.get("recommendation", ""),
        outcome.get("ev_edge_pct", ""),
        outcome.get("betting_pct", 0),
        outcome.get("final_verdict", ""),
        "",  # result - populated after settlement
        "",  # home_team_score - populated after settlement
        "",  # away_team_score - populated after settlement
        "",  # actual stake pct - populated only after placement
        "",  # actual stake amount - populated only after placement
    ]


def prediction_audit_row(match: dict[str, Any]) -> list[Any]:
    return [
        match.get("prediction_timestamp", ""),
        match.get("policy_version", ""),
        match.get("model_version", ""),
        match.get("odds_timestamp", ""),
        match.get("evidence_snapshot_date", ""),
        False,  # bet placed - explicit confirmation is required later
        "",  # actual odds
        "",  # placement timestamp
    ]


def build_requests(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    prediction_sheet_id = int(payload["prediction_sheet_id"])
    start_row_index = int(payload["prediction_start_row"]) - 1
    done_col_index = column_to_index(payload.get("source_done_column", "H"))

    prediction_core_rows = []
    prediction_audit_rows = []
    done_requests = []

    for match in payload.get("matches", []):
        for field in (
            "evidence_grade",
            "prediction_timestamp",
            "policy_version",
            "model_version",
            "odds_timestamp",
            "evidence_snapshot_date",
        ):
            if not match.get(field):
                raise ValueError(
                    f"Match {match.get('id', '<missing id>')} requires {field}"
                )
        outcomes = match.get("outcomes", [])
        if len(outcomes) != 3:
            raise ValueError(
                f"Match {match.get('id', '<missing id>')} must have exactly 3 outcomes"
            )
        real_bets = []
        shadow_bets = []
        for outcome in outcomes:
            if "ev_edge_pct" not in outcome or outcome["ev_edge_pct"] in (None, ""):
                raise ValueError(
                    f"Match {match.get('id', '<missing id>')} outcome "
                    f"{outcome.get('outcome', '<missing outcome>')} requires ev_edge_pct"
                )
            if "betting_pct" not in outcome or outcome["betting_pct"] in (None, ""):
                raise ValueError(
                    f"Match {match.get('id', '<missing id>')} outcome "
                    f"{outcome.get('outcome', '<missing outcome>')} requires betting_pct"
                )
            verdict = str(outcome.get("final_verdict", "")).strip().upper()
            stake = float(outcome["betting_pct"])
            if verdict.startswith("SHADOW BET"):
                shadow_bets.append(outcome)
                if stake != 0:
                    raise ValueError(
                        f"Match {match.get('id', '<missing id>')} shadow bet must have betting_pct 0"
                    )
                edge = float(outcome["ev_edge_pct"])
                odds = float(outcome.get("odds", 0))
                if not 2.0 <= edge <= 10.0 or not odds < 4.0:
                    raise ValueError(
                        f"Match {match.get('id', '<missing id>')} shadow bet must have EV 2-10% and odds below 4.00"
                    )
                if str(match["evidence_grade"]).strip().lower() not in {"medium", "high"}:
                    raise ValueError(
                        f"Match {match.get('id', '<missing id>')} shadow bet requires Medium or High evidence"
                    )
            elif verdict.startswith("BET"):
                real_bets.append(outcome)
                if stake <= 0:
                    raise ValueError(
                        f"Match {match.get('id', '<missing id>')} real bet requires positive betting_pct"
                    )
            elif verdict.startswith("NO BET"):
                if stake != 0:
                    raise ValueError(
                        f"Match {match.get('id', '<missing id>')} no-bet outcome must have betting_pct 0"
                    )
            else:
                raise ValueError(
                    f"Match {match.get('id', '<missing id>')} final_verdict must start with BET, SHADOW BET, or NO BET"
                )
            prediction_core_rows.append(
                {"values": [cell_value(value) for value in prediction_core_row(match, outcome)]}
            )
            prediction_audit_rows.append(
                {"values": [cell_value(value) for value in prediction_audit_row(match)]}
            )

        if len(real_bets) > 1 or len(shadow_bets) > 1:
            raise ValueError(
                f"Match {match.get('id', '<missing id>')} allows at most one BET or SHADOW BET"
            )
        if real_bets and shadow_bets:
            raise ValueError(
                f"Match {match.get('id', '<missing id>')} cannot contain both BET and SHADOW BET"
            )

        done_requests.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": int(match["source_sheet_id"]),
                        "startRowIndex": int(match["source_row"]) - 1,
                        "endRowIndex": int(match["source_row"]),
                        "startColumnIndex": done_col_index,
                        "endColumnIndex": done_col_index + 1,
                    },
                    "cell": {"userEnteredValue": {"boolValue": True}},
                    "fields": "userEnteredValue",
                }
            }
        )

    prediction_requests = []
    if prediction_core_rows:
        prediction_requests.append(
            {
                "updateCells": {
                    "range": {
                        "sheetId": prediction_sheet_id,
                        "startRowIndex": start_row_index,
                        "endRowIndex": start_row_index + len(prediction_core_rows),
                        "startColumnIndex": 0,
                        "endColumnIndex": CORE_COLUMNS,
                    },
                    "rows": prediction_core_rows,
                    "fields": "userEnteredValue",
                }
            }
        )
        prediction_requests.append(
            {
                "updateCells": {
                    "range": {
                        "sheetId": prediction_sheet_id,
                        "startRowIndex": start_row_index,
                        "endRowIndex": start_row_index + len(prediction_audit_rows),
                        "startColumnIndex": AUDIT_START_COLUMN,
                        "endColumnIndex": AUDIT_START_COLUMN + AUDIT_COLUMNS,
                    },
                    "rows": prediction_audit_rows,
                    "fields": "userEnteredValue",
                }
            }
        )

    return {
        "prediction_requests": prediction_requests,
        "done_requests": done_requests,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to prediction payload JSON, or - for stdin")
    args = parser.parse_args()

    if args.input == "-":
        payload = json.loads(sys.stdin.read())
    else:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    print(json.dumps(build_requests(payload), indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
