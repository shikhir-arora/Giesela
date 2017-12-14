"""Testing stuff."""

from giesela.lib import GieselaModule, command


class HelloWorld(GieselaModule):
    """A little script for testing stuff."""

    @command()
    async def hello(self, channel):
        """Hello world."""
        await channel.send("world!")
