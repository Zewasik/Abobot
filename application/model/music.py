from dataclasses import dataclass


@dataclass
class Music:
    """
    The main application Data Transfer Object (DTO)

    Attributes:
        url (str): Song url
        title (str): Song name
        author (str): Song author
        durationSeconds (int): Song duration in seconds
        start_time (float): timestamp at which moment song started playing
        direct_url (str): url containing media source for download
    """
    url: str
    title: str
    author: str
    durationSeconds: int = 0
    start_time: float = 0.0
    direct_url: str = ""
