import asyncio
import random
from datetime import timedelta

import discord
from discord.ext import commands

import config
from application.bot import Bot
from application.context import AppContext
from application.model import MusicQueue
from application.commands import AppCommand


class PlayCommand(AppCommand):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def play(self, ctx: AppContext, link_or_query: str):
        """
        Establishes bot connection to the voice channel where context
        author is located and starts playing requested song
        """

        if not ctx.is_author_connected():
            await ctx.send(f'Необходимо находиться на канале для использования бота')
            return
        if ctx.is_client_connected():
            if not ctx.is_same_channel():
                await ctx.send(f'Бот уже занят:( Он находится в канале **{ctx.voice_client.channel.name}**')
                return
            vc = ctx.voice_client
        else:
            vc = await ctx.author.voice.channel.connect()

        id = ctx.author.guild.id
        if id not in self.bot.queueMap:
            self.bot.queueMap[id] = MusicQueue()

        msg = await ctx.send(f'Попытка добавления трека...')

        video = self.bot.queueMap[id].add_songs(link_or_query)
        if not video['ok'] or video['length'] < 1:
            await msg.edit(content=f"Не удалось добавить трек")
        if video['type'] == "playlist":
            await msg.edit(content=f"Плейлист добавлен в очередь, количество добавленных треков: {video['length']}")
        elif video['type'] == "video":
            await msg.edit(content=f'Трек добавлен в очередь')
        else:
            await msg.edit(content=f"Не удалось добавить трек")

        if vc.is_playing() or vc.is_paused():
            return

        for current_music in self.bot.queueMap[id]:
            if not current_music or not current_music.direct_url:
                continue
            try:
                vc.play(discord.FFmpegPCMAudio(
                    source=current_music.direct_url,
                    before_options=config.CONFIG.ffmpeg_options.before_options,
                    options=config.CONFIG.ffmpeg_options.options)
                )

                await ctx.channel.send(
                    f"Сейчас проигрывается: `{current_music.title}`"
                    f" от **{current_music.author}** [`{timedelta(seconds=current_music.durationSeconds)}`]")
                # vc.source = discord.PCMVolumeTransformer(vc.source, volume=1.0)
            except Exception as e:
                print(f"Error: {e}")

            while vc.is_playing() or vc.is_paused():
                await asyncio.sleep(1)

    @commands.hybrid_command()
    async def gachi(self, ctx: AppContext):
        """Подключает бота к каналу и добавляет в очередь просто шедевры"""
        gachi_url = 'https://www.youtube.com/playlist?list=PLPte1Gs5n0KtXhk3piLJcYK23WJgG4sea'
        await self.play(ctx, gachi_url)

        if self.bot.queueMap[ctx.author.guild.id]:
            random.shuffle(self.bot.queueMap[ctx.author.guild.id].queue)
