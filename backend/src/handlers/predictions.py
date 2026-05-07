import json
from datetime import datetime, timezone

from services import db
from utils import response


def create_prediction(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        user_id = body.get("userId")
        match_id = body.get("matchId")
        predicted_home = body.get("predictedHome")
        predicted_away = body.get("predictedAway")

        if not all([user_id, match_id, predicted_home is not None, predicted_away is not None]):
            return response.error("userId, matchId, predictedHome and predictedAway are required", 400)

        if not isinstance(predicted_home, int) or not isinstance(predicted_away, int):
            return response.error("scores must be whole numbers", 400)

        if predicted_home < 0 or predicted_away < 0:
            return response.error("scores cannot be negative", 400)

        match = db.get_match(match_id)
        if not match:
            return response.error("match not found", 404)

        kickoff = datetime.fromisoformat(match["kickoff"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) >= kickoff:
            return response.error("predictions are locked after kickoff", 403)

        user = db.get_user(user_id)
        if not user:
            return response.error("user not found", 404)

        prediction = {
            "userId": user_id,
            "matchId": match_id,
            "predictedHome": predicted_home,
            "predictedAway": predicted_away,
            "status": "PENDING",
            "points": 0,
            "createdAt": datetime.utcnow().isoformat(),
        }

        db.put_prediction(prediction)
        return response.success(prediction, 201)

    except Exception as e:
        print(f"create_prediction error: {e}")
        return response.error("something went wrong", 500)


def get_predictions(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        user_id = params.get("userId")

        if not user_id:
            return response.error("userId query parameter is required", 400)

        predictions = db.get_predictions_for_user(user_id)

        for prediction in predictions:
            match = db.get_match(prediction["matchId"])
            if match:
                prediction["match"] = match

        predictions.sort(key=lambda p: p.get("match", {}).get("kickoff", ""), reverse=True)
        return response.success({"predictions": predictions})

    except Exception as e:
        print(f"get_predictions error: {e}")
        return response.error("something went wrong", 500)
