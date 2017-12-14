"""Module stuff."""
import inspect
import logging
import re
from functools import wraps

from giesela.models.exceptions import (GieselaException, MissingParamsError,
                                       ParamError)

log = logging.getLogger(__name__)


def command(match=None):
    """Mark as Giesela command."""
    def decorator(func):
        name = func.__name__
        prog = re.compile(match or name)

        sig = inspect.signature(func)
        parameters = sig.parameters

        @wraps(func)
        async def wrapper(self, message):
            content = message.content

            if prog.match(content):
                kwargs = {}

                params = parameters.copy()

                if params.pop("self", False):
                    kwargs["self"] = self

                if params.pop("message", False):
                    kwargs["message"] = message

                if params.pop("guild", False):
                    kwargs["guild"] = message.guild

                if params.pop("channel", False):
                    kwargs["channel"] = message.channel

                if params.pop("author", False):
                    kwargs["author"] = message.author

                if params.pop("content", False):
                    kwargs["content"] = message.content

                for key, param in list(params.items()):
                    if key in message:
                        kwargs[key] = message[key]
                        params.pop(key)
                    elif param.default is inspect.Parameter.empty:
                        log.warning("missing parameter \"{}\"".format(key))

                if params:
                    log.warning("not all parameters satisfied!")
                    raise MissingParamsError(params.keys())

                try:
                    res = await func(**kwargs)
                    return res or True
                except AssertionError as e:
                    if e.args and isinstance(e.args[0], ParamError):
                        raise e.args[0]

                    raise e
            else:
                return False

        setattr(wrapper, "_is_command", True)

        return wrapper

    return decorator


class GieselaModuleMount(type):
    """The metaclass for a module which, when deriving from the inherited class, adds said class to a list."""

    def __init__(cls, name, bases, attrs):
        """Add class to list."""
        if not hasattr(cls, "modules"):
            cls.modules = []
            log.debug("created base Module class")
        else:
            cls.modules.append(cls)
            log.debug("registered module \"{}\"".format(name))


class GieselaModule(metaclass=GieselaModuleMount):
    """A module."""

    singleton = None

    def __init__(self, bot):
        """Initialise module."""
        type(self).singleton = self
        self.bot = bot
        self.config = bot.config
        self.permissions = bot.permissions

        self.commands = {}

        for name, value in inspect.getmembers(self):
            if hasattr(value, "_is_command"):
                self.commands[name] = value

        log.debug("{} registered {} commands".format(self, len(self.commands)))

    def __str__(self):
        """Return string rep. of a Module."""
        return "<Module {}>".format(type(self).__name__)

    async def _on_message(self, message):
        for name, func in self.commands.items():
            try:
                res = await func(message)
                if res:
                    log.debug("{} triggered <{}>: \"{}\"".format(message.author, name, message.content))
            except GieselaException as e:
                # TODO
                raise
            except Exception as e:
                log.exception("Error while running \"{}\"".format(name))

        await self.on_message(message)

    def on_load(self):
        """Call when module loaded."""
        pass

    async def on_ready(self):
        """Call when bot ready."""
        pass

    async def on_error(self, event, *args, **kwargs):
        """Call on error."""
        pass

    async def on_message(self, message):
        """Call when message received."""
        pass

    async def on_message_edit(self, before, after):
        """Call when message edited."""
        pass

    async def on_message_delete(self, message):
        """Call when message deleted."""
        pass

    async def on_channel_create(self, channel):
        """Call when channel created."""
        pass

    async def on_channel_update(self, before, after):
        """Call when channel updated."""
        pass

    async def on_channel_delete(self, channel):
        """Call when channel deleted."""
        pass

    async def on_member_join(self, member):
        """Call when member joined."""
        pass

    async def on_member_remove(self, member):
        """Call when member removed (left)."""
        pass

    async def on_member_update(self, before, after):
        """Call when member updated."""
        pass

    async def on_guild_join(self, guild):
        """Call after joining a guild."""
        pass

    async def on_guild_update(self, before, after):
        """Call when guild updated."""
        pass

    async def on_guild_role_create(self, guild, role):
        """Call when role created."""
        pass

    async def on_guild_role_delete(self, guild, role):
        """Call when role deleted."""
        pass

    async def on_guild_role_update(self, guild, role):
        """Call when role updated."""
        pass

    async def on_voice_state_update(self, before, after):
        """Call when voice state updated."""
        pass

    async def on_member_ban(self, member):
        """Call when member banned."""
        pass

    async def on_member_unban(self, member):
        """Call when member unbanned."""
        pass

    async def on_typing(self, channel, user, when):
        """Call when user starts typing."""
        pass
