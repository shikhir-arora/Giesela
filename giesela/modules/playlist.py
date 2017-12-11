"""Module for controlling playlists."""

from giesela.lib import GieselaModule
from giesela.playlists import PlaylistManager


class Playlist(GieselaModule):
    """Playlist module."""

    def on_load(self):
        """Set playlist manager."""
        self.bot.playlists = PlaylistManager(self.bot)

    async def on_ready(self):
        """Load playlists."""
        await self.bot.playlists.setup()
