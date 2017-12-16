"""The core of Giesela."""

import asyncio
import logging
import traceback
from collections import defaultdict

import aiohttp
import discord

from giesela.config import Config
from giesela.lib import module, reference
from giesela.models import exceptions, signals
from giesela.permissions import PermissionManager
from giesela.utils import localisation

log = logging.getLogger(__name__)


class Giesela(discord.Client):
    """The marvelous Giesela."""

    def __init__(self):
        """Initialise."""
        super().__init__()

        reference.BotReference.bot = self

        self.config = Config.load()
        self.permissions = PermissionManager.load()
        self.modules = []

        self.locks = defaultdict(asyncio.Lock)
        self.aiosession = aiohttp.ClientSession(loop=self.loop)

        self.load_modules()

    def load_modules(self):
        """Load all modules."""
        from . import modules  # noqa: F401

        ext_classes = module.GieselaModule.modules

        self.modules = []

        log.debug("loading {} modules".format(len(ext_classes)))

        for ext_cls in ext_classes:
            try:
                m = ext_cls(self)
                log.debug("created module {}".format(m))

                m.on_load()
                log.debug("initialised module {}".format(m))

                self.modules.append(m)
            except Exception:
                log.error("{}\nCouldn't load extension {}!".format(traceback.format_exc(), ext_cls))

        log.info("loaded {}/{} modules".format(len(self.modules), len(ext_classes)))

    def _cleanup(self):
        try:
            self.loop.run_until_complete(self.logout())
        except Exception:  # Can be ignored
            pass

        pending = asyncio.Task.all_tasks()
        gathered = asyncio.gather(*pending)

        try:
            gathered.cancel()
            self.loop.run_until_complete(gathered)
            gathered.exception()
        except Exception:  # Can be ignored
            pass

    def run(self):
        """Start 'er up."""
        try:
            self.config.check()
        except exceptions.ConfigKeysMissing as e:
            log.error(localisation.format(None, "exceptions.config.missing_keys", " ,".join(e.missing)))
            raise signals.StopSignal

        if not self.config.token:
            log.error(localisation.get(None, "exceptions.token.none"))
            raise signals.StopSignal

        try:
            self.loop.run_until_complete(self.start(self.config.token))
        except discord.errors.LoginFailure:
            log.error(localisation.get(None, "exceptions.token.invalid"))

        finally:
            try:
                self._cleanup()
            except Exception as e:
                log.exception("Error in cleanup:")

            self.loop.close()
            raise signals.StopSignal

    def _emitted(self, future):
        exc = future.exception()

        if exc:
            log.error("Exception in {}:\n{}".format(future, "".join(traceback.format_exception(None, exc, None))))

    async def emit(self, event, *args, **kwargs):
        """Call a function in all extensions."""
        for m in self.modules:
            task = self.loop.create_task(getattr(m, event)(*args, **kwargs))
            task.add_done_callback(self._emitted)

    async def on_connected(self):
        """Call when bot connected to Discord."""
        log.info("connected!")
        await self.emit("on_connected")

    async def on_ready(self):
        """Call when bot ready."""
        log.info("ready!")
        await self.emit("on_ready")

    async def on_resumed(self):
        """Call when the client resumes a session."""
        log.debug("session resumed!")
        await self.emit("on_resumed")

    async def on_error(self, event, *args, **kwargs):
        """Call on error."""
        log.exception("Error in {}".format(event))
        traceback.print_exc()
        await self.emit("on_error", event, *args, **kwargs)

    async def on_typing(self, channel, user, when):
        """Call when user starts typing."""
        await self.emit("on_typing", channel, user, when)

    async def on_message(self, message):
        """Call when message received."""
        await self.emit("_on_message", message)

    async def on_message_delete(self, message):
        """Call when message deleted."""
        await self.emit("on_message_delete", message)

    async def on_message_edit(self, before, after):
        """Call when message edited."""
        await self.emit("on_message_edit", before, after)

    async def on_reaction_add(self, reaction, user):
        """Call when reaction added."""
        await self.emit("on_reaction_add", reaction, user)

    async def on_reaction_remove(self, reaction, user):
        """Call when reaction removed."""
        await self.emit("on_reaction_remove", reaction, user)

    async def on_reaction_clear(self, message, reactions):
        """Call when reaction added."""
        await self.emit("on_reaction_clear", message, reactions)

    async def on_private_channel_create(self, channel):
        """Call when private channel created."""
        await self.emit("on_private_channel_create", channel)

    async def on_private_channel_delete(self, channel):
        """Call when private channel deleted."""
        await self.emit("on_private_channel_delete", channel)

    async def on_private_channel_update(self, before, after):
        """Call when private channel updated."""
        await self.emit("on_private_channel_update", before, after)

    async def on_private_channel_pins_update(self, channel, last_pin):
        """Call when private channel pins updated."""
        await self.emit("on_private_channel_pins_update", channel, last_pin)

    async def on_guild_channel_create(self, channel):
        """Call when channel created in guild."""
        await self.emit("on_guild_channel_create", channel)

    async def on_guild_channel_delete(self, channel):
        """Call when guild channel deleted."""
        await self.emit("on_guild_channel_delete", channel)

    async def on_guild_channel_update(self, before, after):
        """Call when guild channel updated."""
        await self.emit("on_guild_channel_update", before, after)

    async def on_guild_channel_pins_update(self, channel, last_pin):
        """Call when guild channel pins updated."""
        await self.emit("on_guild_channel_pins_update", channel, last_pin)

    async def on_member_join(self, member):
        """Call when member joins guild."""
        await self.emit("on_member_join", member)

    async def on_member_remove(self, member):
        """Call when member leaves guild."""
        await self.emit("on_member_remove", member)

    async def on_member_update(self, before, after):
        """Call when member updates their profile."""
        await self.emit("on_member_update", before, after)

    async def on_guild_join(self, guild):
        """Call when giesela joins guild."""
        await self.emit("on_guild_join", guild)

    async def on_guild_remove(self, guild):
        """Call when giesela leaves guild."""
        await self.emit("on_guild_remove", guild)

    async def on_guild_update(self, before, after):
        """Call when guild is updated."""
        await self.emit("on_guild_update", before, after)

    async def on_guild_role_create(self, role):
        """Call when role created."""
        await self.emit("on_guild_role_create", role)

    async def on_guild_role_delete(self, role):
        """Call when role deleted."""
        await self.emit("on_guild_role_delete", role)

    async def on_guild_role_update(self, before, after):
        """Call when role updated."""
        await self.emit("on_guild_role_update", before, after)

    async def on_guild_emojis_update(self, guild, before, after):
        """Call when guild adds or deletes emoji."""
        await self.emit("on_guild_emojis_update", guild, before, after)

    async def on_guild_available(self, guild):
        """Call when a guild becomes available."""
        await self.emit("on_guild_available", guild)

    async def on_guild_unavailable(self, guild):
        """Call when a guild becomes unavailable."""
        await self.emit("on_guild_unavailable", guild)

    async def on_voice_state_update(self, member, before, after):
        """Call when voice state is updated."""
        await self.emit("on_voice_state_update", member, before, after)

    async def on_member_ban(self, guild, user):
        """Call when a user gets banned from a guild."""
        await self.emit("on_member_ban", guild, user)

    async def on_member_unban(self, guild, user):
        """Call when a user gets unbanned from a guild."""
        await self.emit("on_member_unban", guild, user)
