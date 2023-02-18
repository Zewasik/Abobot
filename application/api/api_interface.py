from abc import abstractmethod
from typing import List, Protocol

from application.model import Music


class MusicApi(Protocol):
    """
    Strategy pattern, which unifies algorithms for supported music sources. (YouTube API, Napster API, etc.)
    """

    @abstractmethod
    def get_song_list(self, url_or_query: str) -> List[Music]:
        """
        :param url_or_query: user's input
        :return List of extracted songs (playlist or single video)
        """
        raise NotImplementedError

    @abstractmethod
    def is_valid_url(self, url: str) -> bool:
        """
        Informs whether API interface can process passed link or not
        :param url:
        """
        raise NotImplementedError

    @abstractmethod
    def get_stream(self, url_to_search: str) -> str:
        """
        :param url_to_search: user's input
        :return: link to the media source
        """
        raise NotImplementedError
