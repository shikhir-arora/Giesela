import datetime
import traceback
from collections import deque
from itertools import islice
from random import shuffle

from youtube_dl.utils import DownloadError, ExtractorError, UnsupportedError

from .entry import StreamPlaylistEntry, URLPlaylistEntry
from .exceptions import ExtractionError, WrongEntryTypeError
from .lib.event_emitter import EventEmitter
from .utils import get_header


class Playlist(EventEmitter):
    """
        A playlist is manages the list of songs that will be played.
    """

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.loop = bot.loop
        self.downloader = bot.downloader
        self.entries = deque()

    def __iter__(self):
        return iter(self.entries)

    def shuffle(self):
        shuffle(self.entries)

    def clear(self):
        self.entries.clear()

    async def add_stream_entry(self, song_url, info=None, **meta):
        if info is None:
            info = {'title': song_url, 'extractor': None}

            try:
                info = await self.downloader.extract_info(self.loop, song_url, download=False)

            except DownloadError as e:
                # ytdl doesn't like it but its probably a stream
                if e.exc_info[0] == UnsupportedError:
                    print("Assuming content is a direct stream")

                elif e.exc_info[0] == URLError:
                    if os.path.exists(os.path.abspath(song_url)):
                        raise ExtractionError(
                            "This is not a stream, this is a file path.")

                    else:  # it might be a file path that just doesn't exist
                        raise ExtractionError(
                            "Invalid input: {0.exc_info[0]}: {0.exc_info[1].reason}".format(e))

                else:
                    # traceback.print_exc()
                    raise ExtractionError("Unknown error: {}".format(e))

            except Exception as e:
                print('Could not extract information from {} ({}), falling back to direct'.format(
                    song_url, e))

        dest_url = song_url
        if info.get('extractor'):
            dest_url = info.get('url')

        if info.get('extractor', None) == 'twitch:stream':  # may need to add other twitch types
            title = info.get('description')
        else:
            title = info.get('title', 'Untitled')

        # TODO: A bit more validation, "~stream some_url" should not just say
        # :ok_hand:

        entry = StreamPlaylistEntry(
            self,
            song_url,
            title,
            destination=dest_url,
            **meta
        )
        self._add_entry(entry)
        return entry, len(self.entries)

    async def add_entry(self, song_url, **meta):
        """
            Validates and adds a song_url to be played. This does not start the download of the song.

            Returns the entry & the position it is in the queue.

            :param song_url: The song url to add to the playlist.
            :param meta: Any additional metadata to add to the playlist entry.
        """

        try:
            info = await self.downloader.extract_info(self.loop, song_url, download=False)
        except Exception as e:
            raise ExtractionError(
                'Could not extract information from {}\n\n{}'.format(song_url, e))

        if not info:
            raise ExtractionError(
                'Could not extract information from %s' % song_url)

        # TODO: Sort out what happens next when this happens
        if info.get('_type', None) == 'playlist':
            raise WrongEntryTypeError("This is a playlist.", True, info.get(
                'webpage_url', None) or info.get('url', None))

        if info['extractor'] in ['generic', 'Dropbox']:
            try:
                # unfortunately this is literally broken
                # https://github.com/KeepSafe/aiohttp/issues/758
                # https://github.com/KeepSafe/aiohttp/issues/852
                content_type = await get_header(self.bot.aiosession, info['url'], 'CONTENT-TYPE')
                print("Got content type", content_type)

            except Exception as e:
                print("[Warning] Failed to get content type for url %s (%s)" % (
                    song_url, e))
                content_type = None

            if content_type:
                if content_type.startswith(('application/', 'image/')):
                    if '/ogg' not in content_type:  # How does a server say `application/ogg` what the actual fuck
                        raise ExtractionError(
                            "Invalid content type \"%s\" for url %s" % (content_type, song_url))

                elif not content_type.startswith(('audio/', 'video/')):
                    print("[Warning] Questionable content type \"%s\" for url %s" % (
                        content_type, song_url))

        entry = URLPlaylistEntry(
            self,
            song_url,
            info.get('title', 'Untitled'),
            info.get('duration', 0) or 0,
            self.downloader.ytdl.prepare_filename(info),
            **meta
        )
        self._add_entry(entry)
        return entry, len(self.entries)

    async def get_entry(self, song_url, **meta):
        try:
            info = await self.downloader.extract_info(self.loop, song_url, download=False)
        except Exception as e:
            raise ExtractionError(
                'Could not extract information from {}\n\n{}'.format(song_url, e))

        if not info:
            raise ExtractionError(
                'Could not extract information from %s' % song_url)

        # TODO: Sort out what happens next when this happens
        if info.get('_type', None) == 'playlist':
            raise WrongEntryTypeError("This is a playlist.", True, info.get(
                'webpage_url', None) or info.get('url', None))

        if info['extractor'] in ['generic', 'Dropbox']:
            try:
                # unfortunately this is literally broken
                # https://github.com/KeepSafe/aiohttp/issues/758
                # https://github.com/KeepSafe/aiohttp/issues/852
                content_type = await get_header(self.bot.aiosession, info['url'], 'CONTENT-TYPE')
                print("Got content type", content_type)

            except Exception as e:
                print("[Warning] Failed to get content type for url %s (%s)" % (
                    song_url, e))
                content_type = None

            if content_type:
                if content_type.startswith(('application/', 'image/')):
                    if '/ogg' not in content_type:  # How does a server say `application/ogg` what the actual fuck
                        raise ExtractionError(
                            "Invalid content type \"%s\" for url %s" % (content_type, song_url))

                elif not content_type.startswith(('audio/', 'video/')):
                    print("[Warning] Questionable content type \"%s\" for url %s" % (
                        content_type, song_url))

        #print ("HEY I GOT THIS: " + self.downloader.ytdl.prepare_filename(info) + "\n\n\n{}\n\n\n".format (str (info)))

        entry = URLPlaylistEntry(
            self,
            song_url,
            info.get('title', 'Untitled'),
            info.get('duration', 0) or 0,
            self.downloader.ytdl.prepare_filename(info),
            **meta
        )
        return entry

    async def add_entry_next(self, song_url, **meta):
        """
            Validates and adds a song_url to be played. This does not start the download of the song.

            Returns the entry & the position it is in the queue.

            :param song_url: The song url to add to the playlist.
            :param meta: Any additional metadata to add to the playlist entry.
        """

        try:
            info = await self.downloader.extract_info(self.loop, song_url, download=False)
        except Exception as e:
            raise ExtractionError(
                'Could not extract information from {}\n\n{}'.format(song_url, e))

        if not info:
            raise ExtractionError(
                'Could not extract information from %s' % song_url)

        # TODO: Sort out what happens next when this happens
        if info.get('_type', None) == 'playlist':
            raise WrongEntryTypeError("This is a playlist.", True, info.get(
                'webpage_url', None) or info.get('url', None))

        if info['extractor'] in ['generic', 'Dropbox']:
            try:
                # unfortunately this is literally broken
                # https://github.com/KeepSafe/aiohttp/issues/758
                # https://github.com/KeepSafe/aiohttp/issues/852
                content_type = await get_header(self.bot.aiosession, info['url'], 'CONTENT-TYPE')
                print("Got content type", content_type)

            except Exception as e:
                print("[Warning] Failed to get content type for url %s (%s)" % (
                    song_url, e))
                content_type = None

            if content_type:
                if content_type.startswith(('application/', 'image/')):
                    if '/ogg' not in content_type:  # How does a server say `application/ogg` what the actual fuck
                        raise ExtractionError(
                            "Invalid content type \"%s\" for url %s" % (content_type, song_url))

                elif not content_type.startswith(('audio/', 'video/')):
                    print("[Warning] Questionable content type \"%s\" for url %s" % (
                        content_type, song_url))

        entry = URLPlaylistEntry(
            self,
            song_url,
            info.get('title', 'Untitled'),
            info.get('duration', 0) or 0,
            self.downloader.ytdl.prepare_filename(info),
            **meta
        )
        self._add_entry_next(entry)
        return entry, len(self.entries)

    async def add_entries(self, entries):
        for entry in entries:
            try:
                await self._add_entry(entry)
            except:
                pass

    async def entries_import_from(self, playlist_url, **meta):
        """
            Imports the songs from `playlist_url` and queues them to be played.

            Returns a list of `entries` that have been enqueued.

            :param playlist_url: The playlist url to be cut into individual urls and added to the playlist
            :param meta: Any additional metadata to add to the playlist entry
        """
        entry_list = []

        try:
            info = await self.downloader.safe_extract_info(self.loop, playlist_url, download=False)
        except Exception as e:
            raise ExtractionError(
                'Could not extract information from {}\n\n{}'.format(playlist_url, e))

        if not info:
            raise ExtractionError(
                'Could not extract information from %s' % playlist_url)

        # Once again, the generic extractor fucks things up.
        if info.get('extractor', None) == 'generic':
            url_field = 'url'
        else:
            url_field = 'webpage_url'

        baditems = 0
        for items in info['entries']:
            if items:
                try:
                    entry = URLPlaylistEntry(
                        self,
                        items[url_field],
                        items.get('title', 'Untitled'),
                        items.get('duration', 0) or 0,
                        self.downloader.ytdl.prepare_filename(items),
                        **meta
                    )
                    entry_list.append(entry)
                except:
                    baditems += 1
                    # Once I know more about what's happening here I can add a
                    # proper message
                    traceback.print_exc()
                    print(items)
                    print("Could not add item")
            else:
                baditems += 1

        if baditems:
            print("Skipped %s bad entries" % baditems)

        return entry_list

    async def entries_async_process_youtube_playlist(self, playlist_url, **meta):
        """
            Processes youtube playlists links from `playlist_url` in a questionable, async fashion.

            :param playlist_url: The playlist url to be cut into individual urls and added to the playlist
            :param meta: Any additional metadata to add to the playlist entry
        """

        try:
            info = await self.downloader.safe_extract_info(self.loop, playlist_url, download=False, process=False)
        except Exception as e:
            raise ExtractionError(
                'Could not extract information from {}\n\n{}'.format(playlist_url, e))

        if not info:
            raise ExtractionError(
                'Could not extract information from %s' % playlist_url)

        gooditems = []
        baditems = 0
        for entry_data in info['entries']:
            if entry_data:
                baseurl = info['webpage_url'].split('playlist?list=')[0]
                song_url = baseurl + 'watch?v=%s' % entry_data['id']

                try:
                    entry = await self.get_entry(song_url, **meta)
                    gooditems.append(entry)
                except ExtractionError:
                    baditems += 1
                except Exception as e:
                    baditems += 1
                    print("There was an error adding the song {}: {}: {}\n".format(
                        entry_data['id'], e.__class__.__name__, e))
            else:
                baditems += 1

        if baditems:
            print("Skipped %s bad entries" % baditems)

        return gooditems

    async def entries_async_process_sc_bc_playlist(self, playlist_url, **meta):
        """
            Processes soundcloud set and bancdamp album links from `playlist_url` in a questionable, async fashion.

            :param playlist_url: The playlist url to be cut into individual urls and added to the playlist
            :param meta: Any additional metadata to add to the playlist entry
        """

        try:
            info = await self.downloader.safe_extract_info(self.loop, playlist_url, download=False, process=False)
        except Exception as e:
            raise ExtractionError(
                'Could not extract information from {}\n\n{}'.format(playlist_url, e))

        if not info:
            raise ExtractionError(
                'Could not extract information from %s' % playlist_url)

        gooditems = []
        baditems = 0
        for entry_data in info['entries']:
            if entry_data:
                song_url = entry_data['url']

                try:
                    entry = await self.get_entry(song_url, **meta)
                    gooditems.append(entry)
                except ExtractionError:
                    baditems += 1
                except Exception as e:
                    baditems += 1
                    print("There was an error adding the song {}: {}: {}\n".format(
                        entry_data['id'], e.__class__.__name__, e))
            else:
                baditems += 1

        if baditems:
            print("Skipped %s bad entries" % baditems)

        return gooditems

    async def import_from(self, playlist_url, **meta):
        """
            Imports the songs from `playlist_url` and queues them to be played.

            Returns a list of `entries` that have been enqueued.

            :param playlist_url: The playlist url to be cut into individual urls and added to the playlist
            :param meta: Any additional metadata to add to the playlist entry
        """
        position = len(self.entries) + 1
        entry_list = []

        try:
            info = await self.downloader.safe_extract_info(self.loop, playlist_url, download=False)
        except Exception as e:
            raise ExtractionError(
                'Could not extract information from {}\n\n{}'.format(playlist_url, e))

        if not info:
            raise ExtractionError(
                'Could not extract information from %s' % playlist_url)

        # Once again, the generic extractor fucks things up.
        if info.get('extractor', None) == 'generic':
            url_field = 'url'
        else:
            url_field = 'webpage_url'

        baditems = 0
        for items in info['entries']:
            if items:
                try:
                    entry = URLPlaylistEntry(
                        self,
                        items[url_field],
                        items.get('title', 'Untitled'),
                        items.get('duration', 0) or 0,
                        self.downloader.ytdl.prepare_filename(items),
                        **meta
                    )

                    self._add_entry(entry)
                    entry_list.append(entry)
                except:
                    baditems += 1
                    # Once I know more about what's happening here I can add a
                    # proper message
                    traceback.print_exc()
                    print(items)
                    print("Could not add item")
            else:
                baditems += 1

        if baditems:
            print("Skipped %s bad entries" % baditems)

        return entry_list, position

    async def async_process_youtube_playlist(self, playlist_url, **meta):
        """
            Processes youtube playlists links from `playlist_url` in a questionable, async fashion.

            :param playlist_url: The playlist url to be cut into individual urls and added to the playlist
            :param meta: Any additional metadata to add to the playlist entry
        """

        try:
            info = await self.downloader.safe_extract_info(self.loop, playlist_url, download=False, process=False)
        except Exception as e:
            raise ExtractionError(
                'Could not extract information from {}\n\n{}'.format(playlist_url, e))

        if not info:
            raise ExtractionError(
                'Could not extract information from %s' % playlist_url)

        gooditems = []
        baditems = 0
        for entry_data in info['entries']:
            if entry_data:
                baseurl = info['webpage_url'].split('playlist?list=')[0]
                song_url = baseurl + 'watch?v=%s' % entry_data['id']

                try:
                    entry, elen = await self.add_entry(song_url, **meta)
                    gooditems.append(entry)
                except ExtractionError:
                    baditems += 1
                except Exception as e:
                    baditems += 1
                    print("There was an error adding the song {}: {}: {}\n".format(
                        entry_data['id'], e.__class__.__name__, e))
            else:
                baditems += 1

        if baditems:
            print("Skipped %s bad entries" % baditems)

        return gooditems

    async def async_process_sc_bc_playlist(self, playlist_url, **meta):
        """
            Processes soundcloud set and bancdamp album links from `playlist_url` in a questionable, async fashion.

            :param playlist_url: The playlist url to be cut into individual urls and added to the playlist
            :param meta: Any additional metadata to add to the playlist entry
        """

        try:
            info = await self.downloader.safe_extract_info(self.loop, playlist_url, download=False, process=False)
        except Exception as e:
            raise ExtractionError(
                'Could not extract information from {}\n\n{}'.format(playlist_url, e))

        if not info:
            raise ExtractionError(
                'Could not extract information from %s' % playlist_url)

        gooditems = []
        baditems = 0
        for entry_data in info['entries']:
            if entry_data:
                song_url = entry_data['url']

                try:
                    entry, elen = await self.add_entry(song_url, **meta)
                    gooditems.append(entry)
                except ExtractionError:
                    baditems += 1
                except Exception as e:
                    baditems += 1
                    print("There was an error adding the song {}: {}: {}\n".format(
                        entry_data['id'], e.__class__.__name__, e))
            else:
                baditems += 1

        if baditems:
            print("Skipped %s bad entries" % baditems)

        return gooditems

    def _add_entry(self, entry):
        self.entries.append(entry)
        self.emit('entry-added', playlist=self, entry=entry)

        if self.peek() is entry:
            entry.get_ready_future()

    def _add_entry_next(self, entry):
        self.entries.insert(0, entry)
        self.emit('entry-added', playlist=self, entry=entry)

        if self.peek() is entry:
            entry.get_ready_future()

    def _add_entry_now(self, entry, player):
        self.entries.insert(0, entry)
        self.emit('entry-added', playlist=self, entry=entry)

        if player.current_entry:
            player.skip()

        if self.peek() is entry:
            entry.get_ready_future()

    def promote_position(self, position):
        rotDist = -1 * (position - 1)
        self.entries.rotate(rotDist)
        entry = self.entries.popleft()
        self.entries.rotate(-1 * rotDist)
        self.entries.appendleft(entry)
        self.emit('entry-added', playlist=self, entry=entry)
        entry.get_ready_future()

        return entry

    def promote_last(self):
        entry = self.entries.pop()
        self.entries.appendleft(entry)
        self.emit('entry-added', playlist=self, entry=entry)
        entry.get_ready_future()

        return entry

    def remove_position(self, position):
        rotDist = -1 * (position - 1)
        self.entries.rotate(rotDist)
        entry = self.entries.popleft()
        self.emit('entry-removed', playlist=self, entry=entry)
        self.entries.rotate(-1 * rotDist)

        return entry

    def remove_first(self):
        entry = self.entries.popleft()
        self.emit('entry-removed', playlist=self, entry=entry)
        entryNext = None
        entryNext = self.peek()

        if entryNext:
            entryNext.get_ready_future()

        return entry

    async def get_next_entry(self, predownload_next=True):
        """
            A coroutine which will return the next song or None if no songs left to play.

            Additionally, if predownload_next is set to True, it will attempt to download the next
            song to be played - so that it's ready by the time we get to it.
        """
        if not self.entries:
            return None

        entry = self.entries.popleft()

        if predownload_next:
            next_entry = self.peek()
            if next_entry:
                next_entry.get_ready_future()

        return await entry.get_ready_future()

    def peek(self):
        """
            Returns the next entry that should be scheduled to be played.
        """
        if self.entries:
            return self.entries[0]

    async def estimate_time_until(self, position, player):
        """
            (very) Roughly estimates the time till the queue will 'position'
        """
        estimated_time = sum(
            [e.duration for e in islice(self.entries, position - 1)])

        # When the player plays a song, it eats the first playlist item, so we
        # just have to add the time back
        if not player.is_stopped and player.current_entry:
            estimated_time += player.current_entry.duration - player.progress

        return datetime.timedelta(seconds=estimated_time)

    def count_for_user(self, user):
        return sum(1 for e in self.entries if e.meta.get('author', None) == user)
