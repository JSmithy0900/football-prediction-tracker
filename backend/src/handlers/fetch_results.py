import os
import boto3

from services import db, football_api, scorer
from utils import response


sns = boto3.client("sns")


def fetch_and_score(event, context):
    try:
        finished_matches = football_api.get_finished_matches()

        if not finished_matches:
            print("no finished matches found")
            return {"scored": 0}

        total_scored = 0

        for match in finished_matches:
            match_id = match["matchId"]
            home_score = match["homeScore"]
            away_score = match["awayScore"]

            db.update_match_result(match_id, home_score, away_score, "FINISHED")

            predictions = db.get_predictions_for_match(match_id)

            for prediction in predictions:
                if prediction.get("status") == "SCORED":
                    continue

                points = scorer.calculate_points(
                    prediction["predictedHome"],
                    prediction["predictedAway"],
                    home_score,
                    away_score,
                )

                db.update_prediction_score(prediction["userId"], match_id, points, "SCORED")
                db.increment_user_points(prediction["userId"], points)

                _send_notification(prediction, match, points)
                total_scored += 1

        print(f"scored {total_scored} predictions")
        return {"scored": total_scored}

    except Exception as e:
        print(f"fetch_and_score error: {e}")
        raise


def _send_notification(prediction, match, points):
    topic_arn = os.environ.get("SNS_TOPIC_ARN")
    if not topic_arn:
        return

    try:
        message = (
            f"{match['homeTeam']} {match['homeScore']}-{match['awayScore']} {match['awayTeam']}\n"
            f"Your prediction: {prediction['predictedHome']}-{prediction['predictedAway']}\n"
            f"Points earned: {points}"
        )

        sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject="Prediction Result",
        )
    except Exception as e:
        print(f"sns notification failed: {e}")
