"""Basic permissions."""


class Permissions:
    """Yaaay I really suck at writing these."""

    __slots__ = ["permissions"]

    def __init__(self, permissions):
        """Initialise."""
        self.permissions = permissions

    def __str__(self):
        """Return str rep."""
        return "<Permissions {} rules>".format(len(self.permissions))

    def grant(self, perm, value=True):
        """Toggle grant for a permissions."""
        self.permissions[perm] = value
