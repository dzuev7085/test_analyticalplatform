"""This module handles hashing of strings."""
import hashlib
import datetime


def create_hash(*kwargs):
    """Create a hash string from an arbitrary list of parameters."""

    joined_string = "".join(str(kwargs))

    return hashlib.md5(joined_string.encode('utf-8')).hexdigest()


def create_hash_string(identifier, reporting_type):
    """Creates a unique hash string.

    We need a way of finding the ReportingTypeInfo record that matches
    a type of change for a certain user on a certain day.

    The chosen solution is to use a hash string. Given the low volume
    the risk of a collision is deemed low."""

    return (datetime.datetime.now().strftime('%Y-%m-%d') +
            identifier +
            str(reporting_type))
