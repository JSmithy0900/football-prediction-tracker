import json
from handlers import leaderboard, users


def create_test_user(username, points=0):
    from services import db
    import uuid
    user = {
        "userId": str(uuid.uuid4()),
        "username": username,
        "totalPoints": points,
        "totalPredictions": 0,
        "createdAt": "2026-01-01T00:00:00",
    }
    db.put_user(user)
    return user


def test_leaderboard_returns_users_ranked(tables):
    create_test_user("jason", points=9)
    create_test_user("smith", points=3)
    create_test_user("jones", points=6)

    event = {"queryStringParameters": {}}
    result = leaderboard.get_leaderboard(event, None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    board = body["leaderboard"]

    assert board[0]["username"] == "jason"
    assert board[0]["rank"] == 1
    assert board[1]["username"] == "jones"
    assert board[2]["username"] == "smith"


def test_leaderboard_empty(tables):
    event = {"queryStringParameters": {}}
    result = leaderboard.get_leaderboard(event, None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["leaderboard"] == []
