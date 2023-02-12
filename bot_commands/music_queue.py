from datetime import timedelta
from typing import List
import time
import yt_dlp
import re

import config


class Video:
    def __init__(self, url, duration, title, author):
        self.url = url
        self.duration = duration if duration else 0
        self.title = title
        self.author = author
        self.start_time = 0.0

    def get_readable_time(self, sec=0) -> str:
        seconds = self.duration if sec <= 0 else sec
        return str(timedelta(seconds=seconds))


class MusicQueue:
    def __init__(self):
        self.queue: list[Video] = list()
        self.now_playing = None

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.queue) > 0:
            ans = self.queue.pop(0)
            ans.start_time = time.time()
            self.now_playing = ans
            try:
                ans.direct_url = get_stream(ans.url)
            except Exception as e:
                print(e)
                return None

            return ans
        else:
            self.now_playing = None
            raise StopIteration

    def add_music(self, query: str) -> dict:
        m = re.search(
            r"(http(s?)://(www\.)?)?youtu(be\.com)/(((watch\?v=[\w-]+)|(playlist\?))(?P<playlist>&?list=[\w-]+)?)?",
            query)
        if m and m.group("playlist"):
            videos = get_videos_from_playlist(m.group(0))
            self.queue.extend(videos)
            return {'ok': True, 'type': 'playlist', 'length': len(videos)}

        video = get_single_video(m.group(0)) if m else search_by_query(query)

        self.queue.append(video)

        return {'ok': True, 'type': 'video', 'length': 1}

    def remove_queue(self):
        self.now_playing = None
        self.queue = list()

    def length(self):
        return len(self.queue)

    def is_empty(self):
        return self.length() < 1


def get_videos_from_playlist(link: str) -> List[Video]:
    result: list[Video] = []

    with yt_dlp.YoutubeDL({'quiet': True, 'ignoreerrors': True}) as ydl:
        playlist = ydl.extract_info(
            link, config.CONFIG.download, process=False)

    if 'entries' not in playlist and '_type' in playlist and 'url' in playlist:
        return get_videos_from_playlist(playlist['url'])
    if 'entries' in playlist:
        for video in playlist['entries']:
            if 'url' in video and 'channel' in video and 'title' in video and 'duration' in video:
                result.append(
                    Video(video['url'], video['duration'], video['title'], video['channel']))

                if len(result) >= config.CONFIG.playlist_limit:
                    break
                continue

            print("не работает")

        return result

    raise NotImplementedError


def get_single_video(url_to_search: str) -> Video:
    with yt_dlp.YoutubeDL({
        'noplaylist': 'True',
        'quiet': True
    }) as ydl:
        video = ydl.extract_info(
            url_to_search, config.CONFIG.download, process=False)
    if 'webpage_url' in video and 'uploader' in video and 'title' in video and 'duration' in video:
        return Video(video['webpage_url'], video['duration'], video['title'], video['uploader'])

    raise NotImplementedError


def get_stream(url_to_search: str) -> str:
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


def search_by_query(query: str) -> Video:
    YDL_OPTIONS = {
        'noplaylist': 'True',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        video = ydl.extract_info(
            f"ytsearch:{query}", config.CONFIG.download, process=False)['entries'].__next__()

    if 'url' in video and 'channel' in video and 'title' in video and 'duration' in video:
        return Video(video['url'], video['duration'], video['title'], video['channel'])

    raise NotImplementedError
