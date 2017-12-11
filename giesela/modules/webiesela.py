"""The web ui."""

from giesela.lib import GieselaModule
from giesela.webiesela import Server


class Webiesela(GieselaModule):
    """The webiesela module."""

    async def on_ready(self):
        """Start server."""
        await Server.serve()
