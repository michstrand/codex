#!/usr/bin/env python3
import argparse
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


LEAGUES = {
    "soccer_denmark_superliga": ("Superliga", "Denmark", "🇩🇰"),
    "soccer_epl": ("Premier League", "England", "🇬🇧"),
    "soccer_france_ligue_one": ("Ligue 1", "France", "🇫🇷"),
    "soccer_germany_bundesliga": ("Bundesliga", "Germany", "🇩🇪"),
    "soccer_spain_la_liga": ("La Liga", "Spain", "🇪🇸"),
    "soccer_italy_serie_a": ("Serie A", "Italy", "🇮🇹"),
}

CODE_OVERRIDES = {
    "hamburger sv": "HSV",
    "paris saint germain": "PSG",
    "paris saint-germain": "PSG",
    "fc bayern munich": "FCB",
    "bayern munich": "BAY",
}


def number(value, field):
    if isinstance(value, str):
        value = value.strip().replace("%", "").replace(",", ".")
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be numeric")


def percentage(value, field):
    raw = number(value, field)
    return raw * 100 if abs(raw) <= 1 else raw


def compact(value):
    return int(value) if float(value).is_integer() else round(value, 2)


def team_code(name):
    key = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    key = re.sub(r"[^a-z0-9 ]+", " ", key)
    key = re.sub(r"\s+", " ", key).strip()
    if key in CODE_OVERRIDES:
        return CODE_OVERRIDES[key]
    tokens = key.split()
    if not tokens:
        raise ValueError("team name cannot be empty")
    first = tokens[0]
    if len(first) <= 3 and len(tokens) > 1:
        return (first + tokens[1][0]).upper()[:3]
    return first.upper()[:3]


def parse_time(value):
    if not value:
        raise ValueError("commence_time is required")
    stamp = str(value).strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(stamp)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ZoneInfo("Europe/Copenhagen"))


def pick_value(row, key):
    value = row.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValueError(f"missing required field: {key}")
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--allow-started", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    source = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    rows = source.get("picks") if isinstance(source, dict) else source
    if not isinstance(rows, list) or not rows:
        raise ValueError("input must contain a nonempty picks array")
    if args.limit < 1:
        raise ValueError("limit must be positive")

    now = datetime.now(timezone.utc)
    matches = []
    seen = set()
    for index, row in enumerate(rows[: args.limit], start=1):
        if not isinstance(row, dict):
            raise ValueError(f"pick {index} must be an object")
        kickoff = parse_time(pick_value(row, "commence_time"))
        if not args.allow_started and kickoff.astimezone(timezone.utc) <= now:
            raise ValueError(f"pick {index} has already started")
        outcome = str(pick_value(row, "outcome")).strip().upper()
        if outcome not in {"1", "X", "2"}:
            raise ValueError(f"pick {index} outcome must be 1, X, or 2")
        match_id = str(pick_value(row, "id")).strip()
        dedupe_key = (match_id, outcome)
        if dedupe_key in seen:
            raise ValueError(f"duplicate pick: {match_id}/{outcome}")
        seen.add(dedupe_key)

        home = str(pick_value(row, "home_team")).strip()
        away = str(pick_value(row, "away_team")).strip()
        odds = number(pick_value(row, "odds"), "odds")
        confidence = percentage(pick_value(row, "true_probability"), "true_probability")
        edge = percentage(pick_value(row, "ev"), "ev")
        raw_stake = number(pick_value(row, "stake_pct"), "stake_pct")
        stake = raw_stake * 100 if 0 < raw_stake < 0.1 else raw_stake
        if odds <= 1 or not 0 < confidence < 100 or stake <= 0:
            raise ValueError(f"pick {index} has invalid odds, probability, or stake")

        sport_key = str(pick_value(row, "sport_key")).strip()
        derived = LEAGUES.get(sport_key)
        if derived is None and not all(row.get(k) for k in ("competition", "country", "flag")):
            raise ValueError(f"unknown sport_key without display overrides: {sport_key}")
        competition, country, flag = derived or (row["competition"], row["country"], row["flag"])
        competition = row.get("competition") or competition
        country = row.get("country") or country
        flag = row.get("flag") or flag
        prediction = "Draw" if outcome == "X" else f"{home if outcome == '1' else away}\nTo Win"

        matches.append({
            "date": f"{kickoff.day} {kickoff.strftime('%b')}",
            "time": kickoff.strftime("%H:%M"),
            "home": home,
            "away": away,
            "homeCode": str(row.get("home_code") or team_code(home)),
            "awayCode": str(row.get("away_code") or team_code(away)),
            "competition": str(competition),
            "country": str(country),
            "flag": str(flag),
            "prediction": prediction,
            "odds": compact(odds),
            "bookmaker": str(pick_value(row, "bookmaker")).strip(),
            "edge": compact(round(edge, 2)),
            "confidence": compact(round(confidence, 2)),
            "stake": f"{compact(round(stake, 2))}%",
        })

    local_now = datetime.now(ZoneInfo("Europe/Copenhagen"))
    result = {
        "updated": f"{local_now.day} {local_now.strftime('%B %Y, %H:%M %Z')}",
        "matches": matches,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(temp.read_text(encoding="utf-8"))
    temp.replace(output)
    print(json.dumps({"output": str(output), "matches": len(matches), "updated": result["updated"]}))


if __name__ == "__main__":
    main()
