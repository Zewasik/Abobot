from discord.ext import commands

import math
from datetime import timedelta

import config
from application.bot import Bot
from application.context import AppContext
from application.model import Music
from application.commands import AppCommand


class ListCommand(AppCommand):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def list(self, ctx: AppContext, page=1):
        """
        Lists paginated music queue
        """

        if not ctx.is_client_connected():
            await ctx.send(f'Бот не подключен')
            return
        if not ctx.is_same_channel():
            await ctx.send(f'Невозможно взаимодействовать с ботом не находясь в канале: {ctx.author.voice.channel.name}')
            return
        if self.bot.queue_is_empty(ctx.author.guild.id):
            await ctx.send(f'Очередь пуста')
            return

        length: int = len(self.bot.queueMap[ctx.author.guild.id])

        pagination_size = config.CONFIG.pagination_size
        last_page = math.ceil(length / pagination_size)
        if page > last_page:
            page = last_page
        elif page < 1:
            page = 1

        start = (page - 1) * pagination_size
        end = page * pagination_size
        end = length if end > length else end

        temp = ""
        for i in range(start, end):
            video: Music = self.bot.queueMap[ctx.author.guild.id].queue[i]
            temp += f'`{i + 1}`. **{video.title}** [`{timedelta(seconds=video.durationSeconds)}`]\n'

        await ctx.send(f'Количество треков в очереди: {length}\n\n{temp}\nСтраница: {page} / {last_page}')
