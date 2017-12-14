"""Permissions for a specific role."""

from .permissions import Permissions


class RolePermissions(Permissions):
    """Permissions for a role."""

    def __init__(self, permissions, role):
        """Initialise role."""
        super().__init__(permissions)

        self.role = role

    def __str__(self):
        """Return fabulous string."""
        return "<Perms for {}, granted by the powerful Giesela>".format(self.role)

    @property
    def level(self):
        """Return the level."""
        return self.role.position

    @classmethod
    def from_dict(cls, data):
        """Build from dict."""
        return cls
