from discord.ext import commands

from application.context import AppContext
from application.model import MusicQueue


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queueMap: dict[int, MusicQueue] = dict()

    async def get_context(self, message, *, cls=AppContext):
        return await super().get_context(message, cls=cls)

    def queue_is_empty(self, ctx: AppContext) -> bool:
        """
        :param ctx: Author's Message Context
        :return: True - queue is empty
        """
        guild_id = ctx.author.guild.id
        return guild_id not in self.queueMap or self.queueMap[guild_id].is_empty()
