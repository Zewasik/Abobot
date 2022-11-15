import asyncio
from pytube import YouTube, Search, Playlist
from discord.ext import commands
import discord
import re
import random

ffmpeg_options = {
    'options': '-bufsize 6000k',
}


class MusicQueue:
    def __init__(self, music_to_add):
        self.queue = list()
        self.add_music(music_to_add)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.queue) > 0:
            ans = get_stream(self.queue.pop(0))
            return ans
        else:
            raise StopIteration

    def add_music(self, query: str):
        m = re.search(
            "(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?", query)
        if m and query.find("list") > 0:
            for url in get_url_from_playlist(query):
                self.queue.append(url)
            return

        parsed_url = m.group(0) if m else search_by_query(query)

        self.queue.append(parsed_url)

    def remove_queue(self):
        self.queue = list()

    def last_track(self):
        return self.queue[-1] if len(self.queue) else "Не удалось загрузить"


def get_url_from_playlist(query: str):
    RECONNECT_NUM = 50

    for i in range(RECONNECT_NUM):
        try:
            playlist = Playlist(query).url_generator()
            return playlist
        except Exception as e:
            print(
                f'Разбитие плейлиста, попытка номер: {i}. Ошибка: {e}.')

    return None


def get_stream(urlToSearch: str):
    RECONNECT_NUM = 50

    for i in range(RECONNECT_NUM):
        try:
            stream = YouTube(urlToSearch).streams.get_by_itag(251)
            return {"url": stream.url, "title": stream.title}
        except Exception as e:
            print(
                f'Получение прямой ссылки, попытка номер: {i}. Ошибка: {e}.')

    return None


def search_by_query(query: str) -> str:
    RECONNECT_NUM = 50

    for i in range(RECONNECT_NUM):
        try:
            s = Search(query).results[0].watch_url
            return s
        except Exception as e:
            print(
                f'Получение ссылки из запроса, попытка номер: {i}. Ошибка: {e}.')

    return None


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"), intents=intents)


class customCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue = dict()

    @commands.hybrid_command()
    async def play(self, ctx: commands.Context, link_or_query):
        """Подключает бота к каналу и добавляет в очередь новую песню по запросу"""
        vc = None

        if not ctx.author.voice:
            await ctx.send(f'Необходимо находиться на канале для использования бота')
            return
        if ctx.voice_client:
            if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
                await ctx.send(f'Бот уже занят:( Он находится в канале {ctx.author.voice.channel.name}')
                return
            vc = ctx.voice_client
        else:
            vc = await ctx.author.voice.channel.connect()

        id = ctx.author.guild.id
        if id in self.queue:
            self.queue[id].add_music(link_or_query)
        else:
            self.queue[id] = MusicQueue(link_or_query)

        await ctx.send(f'Трек(и) добавлен(ы) в очередь, последний: {self.queue[id].last_track()}')

        print(self.queue[id].queue)
        if not vc.is_playing():
            for current_music in self.queue[id]:
                vc.play(discord.FFmpegPCMAudio(
                    executable="ffmpeg", source=current_music['url'], before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"), after=lambda e: print("Music played"))
                await ctx.send(f'Сейчас проигрывается: {current_music["title"]}')
                # vc.source = discord.PCMVolumeTransformer(vc.source, volume=1.0)

                while vc.is_playing():
                    await asyncio.sleep(1)

        return

    @commands.hybrid_command()
    async def skip(self, ctx: commands.Context):
        """Пропускает текущий трек в очереди, если возможно"""

        if ctx.voice_client:
            if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
                await ctx.send(f'Невозможно пропустить трек не находясь в канале: {ctx.author.voice.channel.name}')
                return
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                await ctx.send(f'Пропустил трек')

            return

        await ctx.send(f'Бот не подключен')

    @commands.hybrid_command()
    async def stop(self, ctx: commands.Context):
        """Останавливает проигрывание и очищает очередь"""

        if ctx.voice_client:
            if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
                await ctx.send(f'Невозможно остановить бота не находясь в канале: {ctx.author.voice.channel.name}')
                return
            if ctx.voice_client.is_playing():
                id = ctx.author.guild.id
                if id in self.queue:
                    self.queue[id].remove_queue()
                ctx.voice_client.stop()
                await ctx.send(f'Очередь очищена')

            await ctx.send(f'Очередь уже пуста')
            return

        await ctx.send(f'Бот не подключен')

    @commands.hybrid_command()
    async def disconnect(self, ctx: commands.Context):
        """Отключает бота от канала"""

        if ctx.voice_client:
            if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
                await ctx.send(f'Невозможно отключить бота не находясь в канале: {ctx.author.voice.channel.name}')
                return

            del self.queue[ctx.author.guild.id]
            await ctx.voice_client.disconnect()
            await ctx.send(f'Бот отключен')
            return

        await ctx.send(f'Бот не подключен')

    @commands.hybrid_command()
    async def shuffle(self, ctx: commands.Context):
        """Перемешивает оставшуюся очередь"""

        if ctx.voice_client:
            if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
                await ctx.send(f'Невозможно взаимодействовать с ботом не находясь в канале: {ctx.author.voice.channel.name}')
                return
            random.shuffle(self.queue[ctx.author.guild.id].queue)
            await ctx.send(f'Очередь перемешана')
            return

        await ctx.send(f'Бот не подключен')

    @commands.hybrid_command()
    async def list(self, ctx: commands.Context):
        """Отображает количество трэков в очереди"""

        if ctx.voice_client:
            if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
                await ctx.send(f'Невозможно взаимодействовать с ботом не находясь в канале: {ctx.author.voice.channel.name}')
                return
            length = len(self.queue[ctx.author.guild.id].queue)
            if length < 1:
                await ctx.send(f'Очередь пуста')
                return

            # temp = ""
            # for i, url in enumerate(self.queue[ctx.author.guild.id].queue):
            #     temp += f'{i+1}. {url}\n'
            await ctx.send(f'Количество трэков в очереди: {length}')

            return

        await ctx.send(f'Бот не подключен')


@bot.event
async def on_ready():
    await bot.add_cog(customCommand(bot))
    await bot.tree.sync()
    print("Started")

bot.run(
    'MTAzMzY3NjY3MzM0MzgyMzkwNA.Gh06Dm.IKcYJpyNw-9DwgwbLB-_UFQFJ7GCx-YB38WN8w')
