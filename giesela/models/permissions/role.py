"""Permissions for a specific role."""

from .permissions import Permissions


class RolePermissions(Permissions):
    """Permissions for a role."""

    def __init__(self, permissions, role):
        """Initialise role."""
        super().__init__(permissions)

        self.role = role
