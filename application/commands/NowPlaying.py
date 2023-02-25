import time
from datetime import timedelta

from discord.ext import commands

from application.bot import Bot
from application.context import AppContext
from application.model import Music
from application.commands import AppCommand


class NowPlayingCommand(AppCommand):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def now_playing(self, ctx: AppContext):
        """Displays currently playing (or paused) song"""

        if not ctx.is_client_connected():
            await ctx.send(f'Бот не подключен')
            return
        if not ctx.is_same_channel():
            await ctx.send(f'Невозможно взаимодействовать с ботом не находясь в канале: {ctx.author.voice.channel.name}')
            return
        video: Music = self.bot.queueMap[ctx.author.guild.id].now_playing
        if video:
            temp = f'`{timedelta(seconds=int(time.time() - video.start_time))}`/`{timedelta(seconds=int(video.durationSeconds))}`'
            await ctx.send(f'Сейчас проигрывается: {video.url}. Оставшееся время: {temp}')
            return

        await ctx.send(f'Сейчас ничего не проигрывается')
