import yt_dlp
import asyncio
from discord.ext import commands
import discord
import re
import random

ffmpeg_options = {
    'options': '-bufsize 6000k',
}

DOWNLOAD = False


class Video:
    url = ""
    title = ""
    author = ""
    direct_url = ""
    duration = 0

    def __init__(self, url, duration, title, author):
        self.url = url
        self.duration = duration
        self.title = title
        self.author = author


class MusicQueue:
    def __init__(self):
        self.queue: list[Video] = list()

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.queue) > 0:
            ans = self.queue.pop(0)
            ans.direct_url = get_stream(ans.url)
            return ans
        else:
            raise StopIteration

    def add_music(self, query: str) -> dict:
        m = re.search(
            "(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?", query)
        if m and query.find("list") > 0:
            videos = get_videos_from_playlist(query)
            self.queue.extend(videos)
            return {'ok': True, 'type': 'playlist', 'length': len(videos)}

        video = get_single_video(query) if m else search_by_query(query)

        self.queue.append(video)

        return {'ok': True, 'type': 'video', 'length': 1}

    def remove_queue(self):
        self.queue = list()


def get_videos_from_playlist(link: str):
    result: list[Video] = []

    with yt_dlp.YoutubeDL({'playlistend': 150}) as ydl:
        playlist = ydl.extract_info(
            link, DOWNLOAD, process=False)

    if 'entries' not in playlist and '_type' in playlist and 'url' in playlist:
        return get_videos_from_playlist(playlist['url'])
    if 'entries' in playlist:
        for video in playlist['entries']:
            if 'url' in video and 'channel' in video and 'title' in video and 'duration' in video:
                result.append(
                    Video(video['url'], video['duration'], video['title'], video['channel']))
                continue
            print("не работает")

        return result

    raise NotImplementedError


def get_single_video(urlToSearch: str):
    with yt_dlp.YoutubeDL({
        'noplaylist': 'True'
    }) as ydl:
        video = ydl.extract_info(
            urlToSearch, DOWNLOAD, process=False)
    if 'webpage_url' in video and 'uploader' in video and 'title' in video and 'duration' in video:
        return Video(video['webpage_url'], video['duration'], video['title'], video['uploader'])

    raise NotImplementedError


def get_stream(urlToSearch: str) -> str:
    with yt_dlp.YoutubeDL({
        'format': 'bestaudio/best',
        'f': 251,
        'noplaylist': 'True'
    }) as ydl:
        stream = ydl.extract_info(
            urlToSearch, DOWNLOAD, process=True)
    if 'url' in stream:
        return stream['url']

    raise NotImplementedError


def search_by_query(query: str):
    YDL_OPTIONS = {'noplaylist': 'True'}
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        video = ydl.extract_info(
            f"ytsearch:{query}", DOWNLOAD, process=False)['entries'].__next__()

    if 'url' in video and 'channel' in video and 'title' in video and 'duration' in video:
        return Video(video['url'], video['duration'], video['title'], video['channel'])

    raise NotImplementedError


def getTime(time: int):
    return str(int(time)) if time > 9 else f'0{int(time)}'


def getReadableTime(seconds: int) -> str:
    seconds = seconds if seconds > 0 else 0
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return f'{getTime(hours)}:{getTime(minutes)}:{getTime(seconds)}' if hours > 0 else f'{getTime(minutes)}:{getTime(seconds)}'


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"), intents=intents)


class customCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue: dict[int, MusicQueue] = dict()

    @commands.hybrid_command()
    async def play(self, ctx: commands.Context, link_or_query):
        """Подключает бота к каналу и добавляет в очередь новую песню по запросу"""
        vc = None

        if not ctx.author.voice:
            await ctx.send(f'Необходимо находиться на канале для использования бота')
            return
        if ctx.voice_client:
            if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
                await ctx.send(f'Бот уже занят:( Он находится в канале **{ctx.author.voice.channel.name}**')
                return
            vc = ctx.voice_client
        else:
            vc = await ctx.author.voice.channel.connect()

        id = ctx.author.guild.id
        if id not in self.queue:
            self.queue[id] = MusicQueue()

        await ctx.send(f'Попытка добавления трека...')

        video = self.queue[id].add_music(link_or_query)
        if video['ok'] == False or video['length'] < 1:
            await ctx.channel.send(f"Не удалось добавить трек")
        if video['type'] == "playlist":
            await ctx.channel.send(f"Плейлист добавлен в очередь, количество добавленных треков: {video['length']}")
        elif video['type'] == "video":
            await ctx.channel.send(f'Трек добавлен в очередь')
        else:
            await ctx.channel.send(f'Не удалось добавить трек')

        if not vc.is_playing():
            for current_music in self.queue[id]:
                vc.play(discord.FFmpegPCMAudio(
                    executable="ffmpeg", source=current_music.direct_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"), after=lambda e: print("Music played"))
                await ctx.channel.send(f"Сейчас проигрывается: `{current_music.title}` от **{current_music.author}** [{getReadableTime(current_music.duration)}]")
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

            await ctx.send(f'Количество трэков в очереди: {length}')

            return

        await ctx.send(f'Бот не подключен')


@bot.event
async def on_ready():
    await bot.add_cog(customCommand(bot))
    await bot.tree.sync()
    print("Started")

bot.run(
    'MTA0MjM5MTI4NDMxNDI4MDAyNw.GhbIKt.JVAQcFQGAJTwJk2PyPN3wa9teFjhyBW0bUAp3E')
