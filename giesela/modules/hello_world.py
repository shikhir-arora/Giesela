"""Testing stuff."""

from giesela.lib import GieselaModule, command


class HelloWorld(GieselaModule):
    """A little script for testing stuff."""

    @command(r"^hello\b")
    async def hello(self, channel):
        """Hello world."""
        await self.bot.send_message(channel, "world!")
