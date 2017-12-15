"""Giesela's fancy music player."""

import logging

from discord import FFmpegPCMAudio, PCMVolumeTransformer

from giesela.constants import FileLocations

log = logging.getLogger(__name__)


class Player:
    """The actual player object."""

    def __init__(self):
        """Initialise."""
        self.volume = 0

    def _create_source(self):
        ffmpeg_source = FFmpegPCMAudio(
            "source",
            executable=FileLocations.FFMPEG,
            pipe=False,
            stderr=None,
            before_options=None,
            options=None
        )

        source = PCMVolumeTransformer(ffmpeg_source, volume=self.volume)

        return source
