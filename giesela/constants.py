"""Constants for Giesela."""


class Stats:
    """Various stats."""

    MAJOR = 3  # when you make incompatible API changes
    MINOR = 0  # when you add functionality in a backwards-compatible manner
    PATCH = 0  # when you make backwards-compatible bug fixes

    VERSION = "{}.{}.{}".format(MAJOR, MINOR, PATCH)


class FileLocations:
    """Various files."""

    LOGGING = "config/logging.json"
    CONFIG = "config/config.json"
    PERMISSIONS = "config/permissions.json"

    LOCALISATION = "config/locale.json"
    LOCALE_FOLDER = "locale"

    TOKENS = "data/webiesela_tokens.json"
    EXPIRED_TOKENS = "data/cache/expired_tokens.txt"

    PLAYLISTS = "data/playlists"
