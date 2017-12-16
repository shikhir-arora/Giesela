"""General permissions for a guild."""

from .permissions import Permissions


class GuildPermissions(Permissions):
    """Permissions for a guild."""

    def __init__(self, permissions, guild, roles):
        """Initialise guild."""
        super().__init__(permissions)

        self.guild = guild
        self.roles = roles

    def __str__(self):
        """Return str rep."""
        return "<Perms for {}>".format(self.guild)

    def from_dict(cls, data):
        """Init from dict."""
        return cls
