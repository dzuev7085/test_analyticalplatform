"""This module provides mapping functions."""

OUTLOOK_MAP = {
    1: 1,
    2: 4,
    3: 2,
}


def get_outlook_trend(d):
    """Return outlook trend identifier."""

    return OUTLOOK_MAP[d.decided_lt_outlook]
