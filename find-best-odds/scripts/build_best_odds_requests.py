#!/usr/bin/env python3
"""Build Google Sheets batchUpdate requests for best 1X2 odds columns.

Input tabs use this compact form:
    tab_name:sheet_id:row_count

The generated requests write formulas into L2:R2 for each tab, then copy
those formulas down to the tab's last grid row.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass


START_ROW = 1  # zero-based row 2
START_COL = 11  # zero-based column L
END_COL = 18  # exclusive, through R


FORMULAS = [
    '=IF($G2="";"";IF(MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$E2&""",""price"":([0-9.]+)");".";","));0))))=0;"";MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$E2&""",""price"":([0-9.]+)");".";","));0))))))',
    '=IF($L2="";"";INDEX(FILTER(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(REGEXEXTRACT(b;"^([^""]+)");"")));MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$E2&""",""price"":([0-9.]+)");".";","));0)))=$L2);1))',
    '=IF($G2="";"";IF(MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":""Draw"",""price"":([0-9.]+)");".";","));0))))=0;"";MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":""Draw"",""price"":([0-9.]+)");".";","));0))))))',
    '=IF($N2="";"";INDEX(FILTER(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(REGEXEXTRACT(b;"^([^""]+)");"")));MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":""Draw"",""price"":([0-9.]+)");".";","));0)))=$N2);1))',
    '=IF($G2="";"";IF(MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$F2&""",""price"":([0-9.]+)");".";","));0))))=0;"";MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$F2&""",""price"":([0-9.]+)");".";","));0))))))',
    '=IF($P2="";"";INDEX(FILTER(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(REGEXEXTRACT(b;"^([^""]+)");"")));MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$F2&""",""price"":([0-9.]+)");".";","));0)))=$P2);1))',
    '=AND($L2<>"";$N2<>"";$P2<>"")',
]


@dataclass(frozen=True)
class TabSpec:
    name: str
    sheet_id: int
    row_count: int


def parse_tab_spec(raw: str) -> TabSpec:
    parts = raw.rsplit(":", 2)
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"Invalid tab spec {raw!r}; expected tab_name:sheet_id:row_count"
        )
    name, sheet_id_raw, row_count_raw = parts
    try:
        sheet_id = int(sheet_id_raw)
        row_count = int(row_count_raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid tab spec {raw!r}; sheet_id and row_count must be integers"
        ) from exc
    if not name:
        raise argparse.ArgumentTypeError("Tab name cannot be empty")
    if row_count < 2:
        raise argparse.ArgumentTypeError(f"{name}: row_count must be at least 2")
    return TabSpec(name=name, sheet_id=sheet_id, row_count=row_count)


def update_row_request(tab: TabSpec) -> dict:
    return {
        "updateCells": {
            "range": {
                "sheetId": tab.sheet_id,
                "startRowIndex": START_ROW,
                "endRowIndex": START_ROW + 1,
                "startColumnIndex": START_COL,
                "endColumnIndex": END_COL,
            },
            "rows": [
                {
                    "values": [
                        {"userEnteredValue": {"formulaValue": formula}}
                        for formula in FORMULAS
                    ]
                }
            ],
            "fields": "userEnteredValue",
        }
    }


def copy_down_request(tab: TabSpec) -> dict | None:
    if tab.row_count <= 2:
        return None
    return {
        "copyPaste": {
            "source": {
                "sheetId": tab.sheet_id,
                "startRowIndex": START_ROW,
                "endRowIndex": START_ROW + 1,
                "startColumnIndex": START_COL,
                "endColumnIndex": END_COL,
            },
            "destination": {
                "sheetId": tab.sheet_id,
                "startRowIndex": START_ROW + 1,
                "endRowIndex": tab.row_count,
                "startColumnIndex": START_COL,
                "endColumnIndex": END_COL,
            },
            "pasteType": "PASTE_FORMULA",
            "pasteOrientation": "NORMAL",
        }
    }


def build_requests(tabs: list[TabSpec]) -> list[dict]:
    requests: list[dict] = []
    for tab in tabs:
        requests.append(update_row_request(tab))
        copy_request = copy_down_request(tab)
        if copy_request is not None:
            requests.append(copy_request)
    return requests


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tabs",
        nargs="+",
        type=parse_tab_spec,
        required=True,
        help="One or more tab specs: tab_name:sheet_id:row_count",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    args = parser.parse_args()

    payload = {"requests": build_requests(args.tabs)}
    print(json.dumps(payload, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
