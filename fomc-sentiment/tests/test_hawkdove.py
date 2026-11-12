from fomc_signal.hawkdove import score_text, text_change


def test_hawkish_statement_scores_positive():
    text = ("The Committee decided to raise the target range for the federal funds rate. "
            "Inflation remains elevated. Job gains have been robust and the unemployment rate has remained low. "
            "The Committee anticipates that ongoing increases in the target range will be appropriate.")
    r = score_text(text)
    assert r.score > 0.5
    assert "raise the target" in r.top_hits("hawk", 10)


def test_dovish_statement_scores_negative():
    text = ("The Committee decided to lower the target range for the federal funds rate. "
            "Economic activity has weakened and job gains have slowed. "
            "The Committee will maintain the target range at exceptionally low levels for an extended period.")
    r = score_text(text)
    assert r.score < -0.5


def test_unemployment_direction_is_inverted():
    up = score_text("The unemployment rate has moved up.")
    down = score_text("The unemployment rate declined.")
    assert up.dove > 0 and up.hawk == 0
    assert down.hawk > 0 and down.dove == 0


def test_empty_text_is_neutral():
    assert score_text("").score == 0.0


def test_text_change_bounds():
    assert text_change("a b c", "a b c") == 0.0
    assert text_change(None, "a") != text_change(None, "a")  # NaN
    assert 0 < text_change("a b c d", "a b x y") < 1
