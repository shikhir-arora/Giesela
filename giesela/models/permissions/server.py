"""General permissions for a server."""

from .permissions import Permissions


class ServerPermissions(Permissions):
    """Permissions for a server."""

    def __init__(self, server, roles):
        """Initialise server."""
        super().__init__()

        self.server = server
        self.roles = roles

    def __str__(self):
        """Return str rep."""
        return "<Permissions for {}>".format(self.server)
