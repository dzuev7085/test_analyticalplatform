"""Utils for user profile."""


def get_full_name(self):
    """Override the default representation of a user everywhere
    in the system."""

    return self.first_name + ' ' + self.last_name
