"""Form-field parsing is tolerant: no input should 422 or crash."""

from datetime import date

from tally.stats import current_streak
from tally.web.app import _iso_date, _num, _rating


def test_num_tolerates_blanks_and_junk():
    assert _num("") is None
    assert _num("   ") is None
    assert _num("abc") is None
    assert _num("3100") == 3100.0
    assert _num("4.5") == 4.5


def test_rating_clamps_and_rounds():
    assert _rating("") is None
    assert _rating("4") == 4
    assert _rating("4.5") == 4          # rounds to nearest, banker's rounding -> 4
    assert _rating("9") == 5            # clamped to 5
    assert _rating("0") == 1            # clamped to 1
    assert _rating("five") is None


def test_iso_date_accepts_blank_iso_and_us_format():
    assert _iso_date("") == date.today().isoformat()
    assert _iso_date("2026-06-15") == "2026-06-15"
    assert _iso_date("06/15/2026") == "2026-06-15"
    assert _iso_date("nonsense") == date.today().isoformat()


def test_stats_skip_bad_dates():
    # a malformed date in the DB must not crash the tracker
    assert current_streak(["2026-06-15", "not-a-date"], date(2026, 6, 15)) == 1
