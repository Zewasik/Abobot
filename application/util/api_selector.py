from application.api import MusicApi, YoutubeApi

from typing import (List, Type)


class ApiSelector:
    """
    Singleton class with delayed instancing,
    Gives access to selection of specific MusicApi in runtime
    """
    _instance = None
    _apiImplementations: List[Type[MusicApi]] = []

    def __init__(self):
        if not ApiSelector._instance:
            self._apiImplementations = MusicApi.__subclasses__()
        else:
            print("Instance already created:", self.get_instance())

    @classmethod
    def get_instance(cls):
        """
        Delayed instancing method
        :return: ApiSelector instance class
        """
        if not cls._instance:
            cls._instance = ApiSelector()
        return cls._instance

    def select_api(self, url_or_query: str) -> MusicApi:
        """
        Selects correct API according to user's input string
        :param url_or_query: User's input url or YouTube search query
        :return: specific MusicApi interaction interface
        """
        for api in self._apiImplementations:
            if api().is_valid_url(url=url_or_query):
                return api()
        return YoutubeApi()
