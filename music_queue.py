import yt_dlp
import re


DOWNLOAD = False


def getTime(time: int):
    return str(int(time)) if time > 9 else f'0{int(time)}'


class Video:
    def __init__(self, url, duration, title, author):
        self.url = url
        self.duration = duration if duration else 0
        self.title = title
        self.author = author

    def getReadableTime(self) -> str:
        seconds = self.duration
        seconds = seconds if seconds > 0 else 0
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        return f'{getTime(hours)}:{getTime(minutes)}:{getTime(seconds)}' if hours > 0 else f'{getTime(minutes)}:{getTime(seconds)}'


class MusicQueue:
    def __init__(self):
        self.queue: list[Video] = list()
        self.now_playing = None

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.queue) > 0:
            ans = self.queue.pop(0)
            self.now_playing = ans
            ans.direct_url = get_stream(ans.url)
            return ans
        else:
            self.now_playing = None
            raise StopIteration

    def add_music(self, query: str) -> dict:
        m = re.search(
            "(http(s?)://(www\.)?)?youtu(be\.com)/(((watch\?v=[\w-]+)|(playlist\?))(?P<playlist>&?list=[\w-]+)?)?", query)
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


def get_videos_from_playlist(link: str):
    result: list[Video] = []

    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        playlist = ydl.extract_info(
            link, DOWNLOAD, process=False)

    if 'entries' not in playlist and '_type' in playlist and 'url' in playlist:
        return get_videos_from_playlist(playlist['url'])
    if 'entries' in playlist:
        for video in playlist['entries']:

            if 'url' in video and 'channel' in video and 'title' in video and 'duration' in video:
                result.append(
                    Video(video['url'], video['duration'], video['title'], video['channel']))

                if len(result) > 199:
                    break
                continue

            print("не работает")

        return result

    raise NotImplementedError


def get_single_video(urlToSearch: str):
    with yt_dlp.YoutubeDL({
        'noplaylist': 'True',
        'quiet': True
    }) as ydl:
        video = ydl.extract_info(
            urlToSearch, DOWNLOAD, process=False)
    if 'webpage_url' in video and 'uploader' in video and 'title' in video and 'duration' in video:
        return Video(video['webpage_url'], video['duration'], video['title'], video['uploader'])

    raise NotImplementedError


def get_stream(urlToSearch: str) -> str:
    with yt_dlp.YoutubeDL({
        'format': 'bestaudio/best',
        'f': 251,
        'f': 91,
        'noplaylist': 'True',
        'quiet': True
    }) as ydl:
        stream = ydl.extract_info(
            urlToSearch, DOWNLOAD, process=True)
    if 'url' in stream:
        return stream['url']

    raise NotImplementedError


def search_by_query(query: str):
    YDL_OPTIONS = {
        'noplaylist': 'True',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        video = ydl.extract_info(
            f"ytsearch:{query}", DOWNLOAD, process=False)['entries'].__next__()

    if 'url' in video and 'channel' in video and 'title' in video and 'duration' in video:
        return Video(video['url'], video['duration'], video['title'], video['channel'])

    raise NotImplementedError
