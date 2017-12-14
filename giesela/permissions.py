"""Handling all the permissions stuff."""

import json
import logging

from giesela.constants import FileLocations
from giesela.lib.reference import BotReference

log = logging.getLogger(__name__)


class PermissionManager(BotReference):
    """Permission managment."""

    __slots__ = ["servers"]

    def __init__(self, servers):
        """Init."""
        self.loop = bot.loop  # noqa: F821

        self.servers = servers

        log.info("the flawless permission system is all set!")

    @classmethod
    def load(cls):
        """Load permissions."""
        log.debug("Loading permissions")

        with open(FileLocations.PERMISSIONS, "r") as f:
            data = json.load(f)

        return cls(data)

    def _save(self):
        """Save permissions sync."""
        log.debug("saving permissions")
        data = [server.to_dict() for server in self.servers]

        with open(FileLocations.PERMISSIONS, "w+") as f:
            json.dump(data, f)

        log.info("saved permissions")

    async def save(self):
        """Save permissions asynchronous."""
        await self.loop.run_in_executor(None, self._save)
