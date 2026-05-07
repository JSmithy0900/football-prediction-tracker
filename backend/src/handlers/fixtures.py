from services import db, football_api
from utils import response


def get_fixtures(event, context):
    try:
        fixtures = db.get_matches_by_status("SCHEDULED")

        if not fixtures:
            fixtures = football_api.get_upcoming_fixtures()
            for fixture in fixtures:
                db.put_match(fixture)

        fixtures.sort(key=lambda m: m["kickoff"])
        return response.success({"fixtures": fixtures})

    except Exception as e:
        print(f"get_fixtures error: {e}")
        return response.error("failed to get fixtures", 500)


def sync_fixtures(event, context):
    try:
        fixtures = football_api.get_upcoming_fixtures()

        for fixture in fixtures:
            db.put_match(fixture)

        print(f"synced {len(fixtures)} fixtures")
        return {"synced": len(fixtures)}

    except Exception as e:
        print(f"sync_fixtures error: {e}")
        raise
