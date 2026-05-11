import json
from handlers import users


def make_event(body=None, path_params=None):
    return {
        "body": json.dumps(body) if body else None,
        "pathParameters": path_params or {},
    }


def test_create_user_success(tables):
    event = make_event(body={"username": "jason"})
    result = users.create_user(event, None)

    assert result["statusCode"] == 201
    body = json.loads(result["body"])
    assert body["username"] == "jason"
    assert "userId" in body


def test_create_user_missing_username(tables):
    event = make_event(body={})
    result = users.create_user(event, None)

    assert result["statusCode"] == 400


def test_create_user_username_too_short(tables):
    event = make_event(body={"username": "ab"})
    result = users.create_user(event, None)

    assert result["statusCode"] == 400


def test_create_user_duplicate_username(tables):
    event = make_event(body={"username": "jason"})
    users.create_user(event, None)

    result = users.create_user(event, None)
    assert result["statusCode"] == 409


def test_get_user_success(tables):
    create_event = make_event(body={"username": "jason"})
    created = json.loads(users.create_user(create_event, None)["body"])

    get_event = make_event(path_params={"userId": created["userId"]})
    result = users.get_user(get_event, None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["username"] == "jason"


def test_get_user_not_found(tables):
    event = make_event(path_params={"userId": "does-not-exist"})
    result = users.get_user(event, None)

    assert result["statusCode"] == 404
