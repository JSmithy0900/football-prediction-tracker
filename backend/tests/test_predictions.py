import json
from datetime import datetime, timedelta, timezone
from handlers import predictions, users
from services import db


def make_prediction_event(body=None, params=None):
    return {
        "body": json.dumps(body) if body else None,
        "queryStringParameters": params or {},
    }


def create_test_user(tables, username="jason"):
    event = {"body": json.dumps({"username": username}), "pathParameters": {}}
    result = users.create_user(event, None)
    return json.loads(result["body"])


def create_test_match(tables, minutes_until_kickoff=60):
    kickoff = (datetime.now(timezone.utc) + timedelta(minutes=minutes_until_kickoff)).isoformat()
    match = {
        "matchId": "test-match-1",
        "homeTeam": "Arsenal",
        "awayTeam": "Chelsea",
        "kickoff": kickoff,
        "status": "SCHEDULED",
        "matchday": 1,
        "homeScore": None,
        "awayScore": None,
    }
    db.put_match(match)
    return match


def test_create_prediction_success(tables):
    user = create_test_user(tables)
    match = create_test_match(tables)

    event = make_prediction_event(body={
        "userId": user["userId"],
        "matchId": match["matchId"],
        "predictedHome": 2,
        "predictedAway": 1,
    })

    result = predictions.create_prediction(event, None)
    assert result["statusCode"] == 201
    body = json.loads(result["body"])
    assert body["predictedHome"] == 2
    assert body["status"] == "PENDING"


def test_create_prediction_after_kickoff(tables):
    user = create_test_user(tables)
    create_test_match(tables, minutes_until_kickoff=-10)

    event = make_prediction_event(body={
        "userId": user["userId"],
        "matchId": "test-match-1",
        "predictedHome": 2,
        "predictedAway": 1,
    })

    result = predictions.create_prediction(event, None)
    assert result["statusCode"] == 403


def test_create_prediction_negative_score(tables):
    user = create_test_user(tables)
    create_test_match(tables)

    event = make_prediction_event(body={
        "userId": user["userId"],
        "matchId": "test-match-1",
        "predictedHome": -1,
        "predictedAway": 0,
    })

    result = predictions.create_prediction(event, None)
    assert result["statusCode"] == 400


def test_get_predictions_for_user(tables):
    user = create_test_user(tables)
    create_test_match(tables)

    create_event = make_prediction_event(body={
        "userId": user["userId"],
        "matchId": "test-match-1",
        "predictedHome": 1,
        "predictedAway": 1,
    })
    predictions.create_prediction(create_event, None)

    get_event = make_prediction_event(params={"userId": user["userId"]})
    result = predictions.get_predictions(get_event, None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert len(body["predictions"]) == 1


def test_get_predictions_missing_user_id(tables):
    event = make_prediction_event(params={})
    result = predictions.get_predictions(event, None)

    assert result["statusCode"] == 400
