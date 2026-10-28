
"""Tests for Marathon Registration System."""

import pytest
from marathon_registration import entry_fee, start_wave, finisher_status


# ENTRY FEE TEST CASES

def test_10k_standard():
    assert entry_fee("10k", 30, False, False) == 800


def test_early_bird_discount():
    assert entry_fee("10k", 30, True, False) == 600


def test_senior_citizen_discount():
    assert entry_fee("10k", 65, False, False) == 400


def test_tshirt_fee():
    assert entry_fee("5k", 25, False, True) == 800


def test_half_marathon_fee():
    assert entry_fee("half", 25, False, False) == 1200


def test_full_marathon_fee():
    assert entry_fee("full", 30, False, False) == 1800


def test_unknown_race():
    with pytest.raises(ValueError, match="unknown race"):
        entry_fee("invalid", 25, False, False)


def test_too_young():
    with pytest.raises(ValueError, match="too young"):
        entry_fee("5k", 10, False, False)


def test_underage_half_marathon():
    with pytest.raises(ValueError, match="too young for this distance"):
        entry_fee("half", 16, False, False)


def test_underage_full_marathon():
    with pytest.raises(ValueError, match="too young for this distance"):
        entry_fee("full", 17, False, False)


def test_early_bird_senior_tshirt():
    assert entry_fee("10k", 70, True, True) == 600


# START WAVE TEST CASES

def test_first_timer_wave():
    assert start_wave(None, "full") == "D"


def test_full_marathon_wave_a():
    assert start_wave(180, "full") == "A"


def test_full_marathon_wave_b():
    assert start_wave(220, "full") == "B"


def test_full_marathon_wave_c():
    assert start_wave(300, "full") == "C"


def test_10k_wave_a():
    assert start_wave(80, "10k") == "A"


def test_10k_wave_b():
    assert start_wave(100, "10k") == "B"


def test_10k_wave_c():
    assert start_wave(150, "10k") == "C"


# FINISHER STATUS TEST CASES

def test_disqualified_runner():
    assert finisher_status(100, "half", 1) == "DSQ"


def test_full_marathon_finisher():
    assert finisher_status(350, "full", 0) == "finisher"


def test_full_marathon_dnf():
    assert finisher_status(400, "full", 0) == "DNF"


def test_half_marathon_finisher():
    assert finisher_status(170, "half", 0) == "finisher"


def test_half_marathon_dnf():
    assert finisher_status(200, "half", 0) == "DNF"


def test_5k_finisher():
    assert finisher_status(80, "5k", 0) == "finisher"


def test_5k_dnf():
    assert finisher_status(100, "5k", 0) == "DNF"
