from services import db
from utils import response


def get_leaderboard(event, context):
    try:
        users = db.get_all_users_ranked()

        leaderboard = []
        for rank, user in enumerate(users, start=1):
            leaderboard.append({
                "rank": rank,
                "userId": user["userId"],
                "username": user["username"],
                "totalPoints": int(user.get("totalPoints", 0)),
                "totalPredictions": int(user.get("totalPredictions", 0)),
            })

        return response.success({"leaderboard": leaderboard})

    except Exception as e:
        print(f"get_leaderboard error: {e}")
        return response.error("failed to get leaderboard", 500)
