from services.scorer import calculate_points


def test_exact_score_returns_3_points():
    assert calculate_points(2, 1, 2, 1) == 3


def test_correct_result_returns_1_point():
    assert calculate_points(2, 1, 3, 1) == 1


def test_wrong_result_returns_0_points():
    assert calculate_points(2, 1, 1, 2) == 0


def test_exact_draw_returns_3_points():
    assert calculate_points(0, 0, 0, 0) == 3


def test_correct_draw_returns_1_point():
    assert calculate_points(1, 1, 2, 2) == 1


def test_correct_away_win_returns_1_point():
    assert calculate_points(0, 2, 1, 3) == 1


def test_no_score_returns_0_points():
    assert calculate_points(1, 0, None, None) == 0
