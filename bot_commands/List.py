from discord.ext import commands
from bot_commands.bot_wrapper import BotWrapper
import bot_commands.helpers as helpers
import math

import config


class ListCommand(commands.Cog):
    def __init__(self, bot: BotWrapper):
        self.bot = bot

    @commands.hybrid_command()
    async def list(self, ctx: commands.Context, page=1):
        """Отображает заданное в config.pagintion_size число треков в очереди с n-страницы"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно взаимодействовать с ботом не находясь в канале: {ctx.author.voice.channel.name}')
            return
        if helpers.queue_is_empty(ctx, self.bot.queue):
            await ctx.send(f'Очередь пуста')
            return

        length = self.bot.queue[ctx.author.guild.id].length()

        pagination_size = config.CONFIG.pagination_size
        last_page = math.ceil(length / pagination_size)
        if page > last_page:
            page = last_page
        elif page < 1:
            page = 1

        start = (page-1) * pagination_size
        end = page * pagination_size
        end = length if end > length else end

        temp = ""
        for i in range(start, end):
            video = self.bot.queue[ctx.author.guild.id].queue[i]
            temp += f'`{i+1}`. **{video.title}** [`{video.get_readable_time()}`]\n'

        await ctx.send(f'Количество треков в очереди: {length}\n\n{temp}\nСтраница: {page} / {last_page}')
