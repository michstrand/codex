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
      "outcomes": [
        {
          "outcome": "1",
          "odds": 5.2,
          "bookmaker": "Betfair",
          "implied_probability": "19.2%",
          "recommendation": "No bet...",
          "final_verdict": "0 units..."
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


PREDICTION_COLUMNS = 13


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


def prediction_row(match: dict[str, Any], outcome: dict[str, Any]) -> list[Any]:
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
        outcome.get("final_verdict", ""),
    ]


def build_requests(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    prediction_sheet_id = int(payload["prediction_sheet_id"])
    start_row_index = int(payload["prediction_start_row"]) - 1
    done_col_index = column_to_index(payload.get("source_done_column", "H"))

    prediction_rows = []
    done_requests = []

    for match in payload.get("matches", []):
        outcomes = match.get("outcomes", [])
        if len(outcomes) != 3:
            raise ValueError(
                f"Match {match.get('id', '<missing id>')} must have exactly 3 outcomes"
            )
        for outcome in outcomes:
            prediction_rows.append(
                {"values": [cell_value(value) for value in prediction_row(match, outcome)]}
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
    if prediction_rows:
        prediction_requests.append(
            {
                "updateCells": {
                    "range": {
                        "sheetId": prediction_sheet_id,
                        "startRowIndex": start_row_index,
                        "endRowIndex": start_row_index + len(prediction_rows),
                        "startColumnIndex": 0,
                        "endColumnIndex": PREDICTION_COLUMNS,
                    },
                    "rows": prediction_rows,
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
