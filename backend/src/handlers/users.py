import json
import uuid
from datetime import datetime

from services import db
from utils import response


def create_user(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        username = body.get("username", "").strip()

        if not username:
            return response.error("username is required", 400)

        if len(username) < 3 or len(username) > 20:
            return response.error("username must be between 3 and 20 characters", 400)

        existing = db.get_user_by_username(username)
        if existing:
            return response.error("username already taken", 409)

        user = {
            "userId": str(uuid.uuid4()),
            "username": username,
            "totalPoints": 0,
            "totalPredictions": 0,
            "createdAt": datetime.utcnow().isoformat(),
        }

        db.put_user(user)
        return response.success(user, 201)

    except Exception as e:
        print(f"create_user error: {e}")
        return response.error("something went wrong", 500)


def get_user(event, context):
    try:
        user_id = event.get("pathParameters", {}).get("userId")

        if not user_id:
            return response.error("userId is required", 400)

        user = db.get_user(user_id)

        if not user:
            return response.error("user not found", 404)

        return response.success(user)

    except Exception as e:
        print(f"get_user error: {e}")
        return response.error("something went wrong", 500)
