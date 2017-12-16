"""Debug stuff."""

from giesela.lib import GieselaModule, command


class Debug(GieselaModule):
    """Debugging module."""

    @command(r"^execute\b")
    async def execute(self, channel):
        """Debug stuff."""
        await channel.send("not even remotely implemented")
