import time
import random
from typing import List, Union

from application.api import MusicApi
from application.model import Music
from application.util import ApiSelector


class MusicQueue:
    """
    An iterable collection, containing server's pending to play songs
    """

    def __init__(self):
        self.queue: List[Music] = list()
        self.now_playing: Union[Music, None] = None
        self.selector: ApiSelector = ApiSelector.get_instance()

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.queue) > 0:
            ans: Music = self.queue.pop(0)
            ans.start_time = time.time()
            self.now_playing = ans
            try:
                api: MusicApi = self.selector.select_api(ans.url)
                ans.direct_url = api.get_stream(ans.url)
            except Exception as e:
                print(e)
                return None

            return ans
        else:
            self.now_playing = None
            raise StopIteration

    def __len__(self):
        return len(self.queue)

    def add_songs(self, query: str) -> dict:
        """
        Adding songs in pending queue
        :param query: provided by user link to supported service or YouTube search query
        :return: dict, containing success status, link type, and number of added songs
        """
        api: MusicApi = self.selector.select_api(query)
        videos: List[Music] = api.get_song_list(query)
        self.queue.extend(videos)
        return {
            'ok': True,
            'type': 'playlist' if len(videos) > 1 else 'video',
            'length': len(videos)
        }

    def shuffle(self) -> None:
        """
        Shuffles music queue
        """
        random.shuffle(self.queue)

    def clean(self) -> None:
        """
        Cleaning queue
        """
        self.now_playing = None
        self.queue = list()

    def is_empty(self) -> bool:
        """
        :return: True - empty queue
        """
        return len(self) == 0
