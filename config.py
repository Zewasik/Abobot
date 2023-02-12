from dataclasses import dataclass


@dataclass
class FFmpegConfiguration:
    before_options: str
    options: str


@dataclass
class Configuration:
    download: bool
    playlist_limit: int
    pagination_size: int
    ffmpeg_options: FFmpegConfiguration


global CONFIG
CONFIG = {}
