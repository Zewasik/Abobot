import re
from typing import List

import yt_dlp

import config
from application.api import MusicApi
from application.model import Music


class YoutubeApi(MusicApi):
    """
    Implementation of MusicApi interface for YouTube videos
    """

    _url_regex: str = \
        r"(http(s?)://(www\.)?)?youtu(be\.com)/(((watch\?v=[\w-]+)|(playlist\?))(?P<playlist>&?list=[\w-]+)?)?"

    def get_song_list(self, url_or_query: str) -> List[Music]:
        m = re.search(self._url_regex, url_or_query)
        if m and m.group("playlist"):
            return self.__get_videos_from_playlist(m.group(0))
        return [self.__get_single_video(m.group(0)) if m else self.__search_by_query(url_or_query)]

    def is_valid_url(self, url: str) -> bool:
        return bool(re.search(self._url_regex, url))

    def get_stream(self, url_to_search: str) -> str:
        with yt_dlp.YoutubeDL({
            'format': 'bestaudio/best',
            'f': 251,
            'f': 91,
            'noplaylist': 'True',
            'quiet': True
        }) as ydl:
            stream = ydl.extract_info(
                url_to_search, config.CONFIG.download, process=True)
        if 'url' in stream:
            return stream['url']

        raise NotImplementedError

    def __get_videos_from_playlist(self, url: str) -> List[Music]:
        result: list[Music] = []

        with yt_dlp.YoutubeDL({'quiet': True, 'ignoreerrors': True}) as ydl:
            playlist = ydl.extract_info(
                url, config.CONFIG.download, process=False)

        if 'entries' not in playlist and '_type' in playlist and 'url' in playlist:
            return self.__get_videos_from_playlist(playlist['url'])
        if 'entries' in playlist:
            for video in playlist['entries']:
                if 'url' in video and 'channel' in video and 'title' in video and 'duration' in video:
                    result.append(
                        Music(
                            url=video['url'],
                            title=video['title'],
                            author=video['channel'],
                            durationSeconds=video['duration']
                        )
                    )
                    if len(result) >= config.CONFIG.playlist_limit:
                        break
                    continue

                print("не работает")

            return result

        raise NotImplementedError

    def __get_single_video(self, url_to_search: str) -> Music:
        with yt_dlp.YoutubeDL({
            'noplaylist': 'True',
            'quiet': True
        }) as ydl:
            video = ydl.extract_info(
                url_to_search, config.CONFIG.download, process=False)
        if 'webpage_url' in video and 'uploader' in video and 'title' in video and 'duration' in video:
            return Music(
                url=video['webpage_url'],
                title=video['title'],
                author=video['uploader'],
                durationSeconds=video['duration']
            )

        raise NotImplementedError

    def __search_by_query(self, query: str) -> Music:
        YDL_OPTIONS = {
            'noplaylist': 'True',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            video = ydl.extract_info(
                f"ytsearch:{query}", config.CONFIG.download, process=False)['entries'].__next__()
        if 'url' in video and 'channel' in video and 'title' in video and 'duration' in video:
            return Music(
                url=video['url'],
                title=video['title'],
                author=video['channel'],
                durationSeconds=video['duration']
            )

        raise NotImplementedError
