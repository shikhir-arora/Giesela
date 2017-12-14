"""Handling all the permissions stuff."""

import json
import logging

from giesela.constants import FileLocations
from giesela.lib.reference import BotReference

log = logging.getLogger(__name__)


class PermissionManager(BotReference):
    """Permission managment."""

    __slots__ = ["guilds"]

    def __init__(self, guilds):
        """Init."""
        self.loop = bot.loop  # noqa: F821

        self.guilds = guilds

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
        data = [guild.to_dict() for guild in self.guilds]

        with open(FileLocations.PERMISSIONS, "w+") as f:
            json.dump(data, f)

        log.info("saved permissions")

    async def save(self):
        """Save permissions asynchronous."""
        await self.loop.run_in_executor(None, self._save)
