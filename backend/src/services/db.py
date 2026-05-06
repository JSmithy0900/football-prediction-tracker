import os
import boto3
from boto3.dynamodb.conditions import Key, Attr


dynamodb = boto3.resource("dynamodb")

matches_table = dynamodb.Table(os.environ["MATCHES_TABLE"])
predictions_table = dynamodb.Table(os.environ["PREDICTIONS_TABLE"])
users_table = dynamodb.Table(os.environ["USERS_TABLE"])


# Matches

def get_match(match_id):
    resp = matches_table.get_item(Key={"matchId": match_id})
    return resp.get("Item")


def put_match(item):
    matches_table.put_item(Item=item)


def get_matches_by_status(status):
    resp = matches_table.query(
        IndexName="StatusIndex",
        KeyConditionExpression=Key("status").eq(status),
    )
    return resp.get("Items", [])


def update_match_result(match_id, home_score, away_score, status):
    matches_table.update_item(
        Key={"matchId": match_id},
        UpdateExpression="SET homeScore = :h, awayScore = :a, #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":h": home_score, ":a": away_score, ":s": status},
    )


# Predictions

def get_prediction(user_id, match_id):
    resp = predictions_table.get_item(Key={"userId": user_id, "matchId": match_id})
    return resp.get("Item")


def put_prediction(item):
    predictions_table.put_item(Item=item)


def get_predictions_for_user(user_id):
    resp = predictions_table.query(
        KeyConditionExpression=Key("userId").eq(user_id),
    )
    return resp.get("Items", [])


def get_predictions_for_match(match_id):
    resp = predictions_table.query(
        IndexName="MatchIndex",
        KeyConditionExpression=Key("matchId").eq(match_id),
    )
    return resp.get("Items", [])


def update_prediction_score(user_id, match_id, points, status):
    predictions_table.update_item(
        Key={"userId": user_id, "matchId": match_id},
        UpdateExpression="SET points = :p, #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":p": points, ":s": status},
    )


# Users

def get_user(user_id):
    resp = users_table.get_item(Key={"userId": user_id})
    return resp.get("Item")


def get_user_by_username(username):
    resp = users_table.query(
        IndexName="UsernameIndex",
        KeyConditionExpression=Key("username").eq(username),
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def put_user(item):
    users_table.put_item(Item=item)


def increment_user_points(user_id, points):
    users_table.update_item(
        Key={"userId": user_id},
        UpdateExpression="ADD totalPoints :p, totalPredictions :one SET leaderboardPartition = :lp",
        ExpressionAttributeValues={":p": points, ":one": 1, ":lp": "ALL"},
    )


def get_all_users_ranked():
    resp = users_table.scan(
        FilterExpression=Attr("totalPoints").exists(),
    )
    users = resp.get("Items", [])
    return sorted(users, key=lambda u: int(u.get("totalPoints", 0)), reverse=True)
