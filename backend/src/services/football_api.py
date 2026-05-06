import os
import requests
from datetime import datetime, timedelta

BASE_URL = "https://api.football-data.org/v4"
COMPETITION = "PL"


def _headers():
    return {"X-Auth-Token": os.environ["FOOTBALL_API_KEY"]}


def get_upcoming_fixtures(days_ahead=7):
    date_from = datetime.utcnow().strftime("%Y-%m-%d")
    date_to = (datetime.utcnow() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    response = requests.get(
        f"{BASE_URL}/competitions/{COMPETITION}/matches",
        headers=_headers(),
        params={
            "status": "SCHEDULED",
            "dateFrom": date_from,
            "dateTo": date_to,
        },
    )
    response.raise_for_status()
    return [_format_match(m) for m in response.json().get("matches", [])]


def get_finished_matches(days_back=2):
    date_from = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    date_to = datetime.utcnow().strftime("%Y-%m-%d")

    response = requests.get(
        f"{BASE_URL}/competitions/{COMPETITION}/matches",
        headers=_headers(),
        params={
            "status": "FINISHED",
            "dateFrom": date_from,
            "dateTo": date_to,
        },
    )
    response.raise_for_status()
    return [_format_match(m) for m in response.json().get("matches", [])]


def _format_match(match):
    return {
        "matchId": str(match["id"]),
        "homeTeam": match["homeTeam"]["shortName"],
        "awayTeam": match["awayTeam"]["shortName"],
        "kickoff": match["utcDate"],
        "status": match["status"],
        "matchday": match.get("matchday"),
        "homeScore": match["score"]["fullTime"].get("home"),
        "awayScore": match["score"]["fullTime"].get("away"),
    }
