def calculate_points(predicted_home, predicted_away, actual_home, actual_away):
    if actual_home is None or actual_away is None:
        return 0

    predicted_home = int(predicted_home)
    predicted_away = int(predicted_away)
    actual_home = int(actual_home)
    actual_away = int(actual_away)

    if predicted_home == actual_home and predicted_away == actual_away:
        return 3

    if _get_result(predicted_home, predicted_away) == _get_result(actual_home, actual_away):
        return 1

    return 0


def _get_result(home, away):
    if home > away:
        return "home"
    if away > home:
        return "away"
    return "draw"
