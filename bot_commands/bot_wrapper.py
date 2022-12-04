from bot_commands.music_queue import MusicQueue
from discord.ext import commands


class BotWrapper(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue: dict[int, MusicQueue] = dict()
