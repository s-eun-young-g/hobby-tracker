"""Tests for the pure stats functions."""

from datetime import date

from tally.stats import best_score, current_streak, heatmap, longest_streak


def test_current_streak_counts_back_from_today():
    d = ["2026-06-13", "2026-06-14", "2026-06-15"]
    assert current_streak(d, date(2026, 6, 15)) == 3


def test_current_streak_allows_yesterday():
    d = ["2026-06-13", "2026-06-14"]
    assert current_streak(d, date(2026, 6, 15)) == 2   # logged through yesterday


def test_current_streak_broken():
    d = ["2026-06-10", "2026-06-11"]
    assert current_streak(d, date(2026, 6, 15)) == 0


def test_current_streak_ignores_duplicates():
    d = ["2026-06-14", "2026-06-14", "2026-06-15"]
    assert current_streak(d, date(2026, 6, 15)) == 2


def test_longest_streak():
    d = ["2026-06-01", "2026-06-02", "2026-06-03", "2026-06-10", "2026-06-11"]
    assert longest_streak(d) == 3


def test_best_score_direction():
    assert best_score([40, 55, 12], "high") == 55
    assert best_score([40, 55, 12], "low") == 12      # e.g. crossword seconds
    assert best_score([40, 55], None) is None          # hobby has no score


def test_heatmap_length_and_counts():
    hm = heatmap(["2026-06-15", "2026-06-15", "2026-06-14"], date(2026, 6, 15), days=7)
    assert len(hm) == 7
    assert hm[-1] == ("2026-06-15", 2)
    assert hm[-2] == ("2026-06-14", 1)
    assert hm[0][1] == 0
