import os
import sys
import boto3
import pytest
from moto import mock_aws

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

os.environ["MATCHES_TABLE"] = "spt-matches-test"
os.environ["PREDICTIONS_TABLE"] = "spt-predictions-test"
os.environ["USERS_TABLE"] = "spt-users-test"
os.environ["FOOTBALL_API_KEY"] = "test-key"
os.environ["SNS_TOPIC_ARN"] = ""
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"


@pytest.fixture
def aws():
    with mock_aws():
        yield


@pytest.fixture
def tables(aws):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

    dynamodb.create_table(
        TableName="spt-matches-test",
        BillingMode="PAY_PER_REQUEST",
        AttributeDefinitions=[
            {"AttributeName": "matchId", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
            {"AttributeName": "kickoff", "AttributeType": "S"},
        ],
        KeySchema=[{"AttributeName": "matchId", "KeyType": "HASH"}],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "StatusIndex",
                "KeySchema": [
                    {"AttributeName": "status", "KeyType": "HASH"},
                    {"AttributeName": "kickoff", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )

    dynamodb.create_table(
        TableName="spt-predictions-test",
        BillingMode="PAY_PER_REQUEST",
        AttributeDefinitions=[
            {"AttributeName": "userId", "AttributeType": "S"},
            {"AttributeName": "matchId", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "userId", "KeyType": "HASH"},
            {"AttributeName": "matchId", "KeyType": "RANGE"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "MatchIndex",
                "KeySchema": [
                    {"AttributeName": "matchId", "KeyType": "HASH"},
                    {"AttributeName": "userId", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )

    dynamodb.create_table(
        TableName="spt-users-test",
        BillingMode="PAY_PER_REQUEST",
        AttributeDefinitions=[
            {"AttributeName": "userId", "AttributeType": "S"},
            {"AttributeName": "username", "AttributeType": "S"},
        ],
        KeySchema=[{"AttributeName": "userId", "KeyType": "HASH"}],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "UsernameIndex",
                "KeySchema": [{"AttributeName": "username", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )

    yield dynamodb
