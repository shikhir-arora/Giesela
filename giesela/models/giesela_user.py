"""More functionality."""

from giesela.lib.reference import BotReference


class GieselaUser(BotReference):
    """A Giesela user."""

    __slots__ = ["discord_id", "name", "discriminator", "avatar_url", "guild", "guild_id", "guild_name", "member"]

    users = {}

    def __init__(self, discord_id, discriminator, name, avatar_url, guild, guild_id, guild_name, member):
        """Create a new Giesela user."""
        self.discord_id = discord_id
        self.name = name
        self.discriminator = discriminator
        self.avatar_url = avatar_url

        self.guild = guild
        self.guild_id = guild_id
        self.guild_name = guild_name

        self.member = member

    def __str__(self):
        """Return a string version."""
        return "{}@[{}]".format(self.tag, self.guild_name)

    @classmethod
    def _cache_user(cls, member):
        cache_key = "{}@{}".format(member.id, member.guild.id)

        if cache_key not in cls.users:
            cls.users[cache_key] = cls(member.id, member.discriminator, member.name, member.avatar_url, member.guild, member.guild.id, member.guild.name, member)

        return cls.users[cache_key]

    @classmethod
    def from_member(cls, member):
        """Create a new instance based on its Discord counterpart."""
        return cls._cache_user(member)

    @classmethod
    def from_dict(cls, data):
        """Load instance from a serialised dict."""
        guild = cls.bot.get_guild(data["guild"]["id"])
        member = guild.get_member(data["id"])
        return cls.from_member(member)

    @property
    def tag(self):
        """Return the discord tag."""
        return "{}#{}".format(self.name, self.discriminator)

    def to_dict(self):
        """Convert to a serialised dict."""
        return {
            "id": self.discord_id,
            "name": self.name,
            "tag": self.tag,
            "avatar_url": self.avatar_url,
            "guild": {
                "id": self.guild_id,
                "name": self.guild_name,
            }
        }
