import os
import boto3
from boto3.dynamodb.conditions import Key, Attr


def _table(env_key):
    return boto3.resource("dynamodb").Table(os.environ[env_key])


def _matches():
    return _table("MATCHES_TABLE")


def _predictions():
    return _table("PREDICTIONS_TABLE")


def _users():
    return _table("USERS_TABLE")


# Matches

def get_match(match_id):
    resp = _matches().get_item(Key={"matchId": match_id})
    return resp.get("Item")


def put_match(item):
    _matches().put_item(Item=item)


def get_matches_by_status(status):
    resp = _matches().query(
        IndexName="StatusIndex",
        KeyConditionExpression=Key("status").eq(status),
    )
    return resp.get("Items", [])


def update_match_result(match_id, home_score, away_score, status):
    _matches().update_item(
        Key={"matchId": match_id},
        UpdateExpression="SET homeScore = :h, awayScore = :a, #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":h": home_score, ":a": away_score, ":s": status},
    )


# Predictions

def get_prediction(user_id, match_id):
    resp = _predictions().get_item(Key={"userId": user_id, "matchId": match_id})
    return resp.get("Item")


def put_prediction(item):
    _predictions().put_item(Item=item)


def get_predictions_for_user(user_id):
    resp = _predictions().query(
        KeyConditionExpression=Key("userId").eq(user_id),
    )
    return resp.get("Items", [])


def get_predictions_for_match(match_id):
    resp = _predictions().query(
        IndexName="MatchIndex",
        KeyConditionExpression=Key("matchId").eq(match_id),
    )
    return resp.get("Items", [])


def update_prediction_score(user_id, match_id, points, status):
    _predictions().update_item(
        Key={"userId": user_id, "matchId": match_id},
        UpdateExpression="SET points = :p, #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":p": points, ":s": status},
    )


# Users

def get_user(user_id):
    resp = _users().get_item(Key={"userId": user_id})
    return resp.get("Item")


def get_user_by_username(username):
    resp = _users().query(
        IndexName="UsernameIndex",
        KeyConditionExpression=Key("username").eq(username),
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def put_user(item):
    _users().put_item(Item=item)


def increment_user_points(user_id, points):
    _users().update_item(
        Key={"userId": user_id},
        UpdateExpression="ADD totalPoints :p, totalPredictions :one",
        ExpressionAttributeValues={":p": points, ":one": 1},
    )


def get_all_users_ranked():
    resp = _users().scan(
        FilterExpression=Attr("totalPoints").exists(),
    )
    users = resp.get("Items", [])
    return sorted(users, key=lambda u: int(u.get("totalPoints", 0)), reverse=True)
