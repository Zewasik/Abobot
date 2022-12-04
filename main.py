import math
import os
import asyncio
from music_queue import MusicQueue
from discord.ext import commands, tasks
import discord
import random
import helpers
from dotenv import load_dotenv
from music_queue import MusicQueue

ffmpeg_options = {
    'before_options': "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    'options': "-v panic"
}

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

        if not helpers.author_is_connected(ctx):
            await ctx.send(f'Необходимо находиться на канале для использования бота')
            return
        if helpers.bot_is_connected(ctx):
            if not helpers.is_same_channel(ctx):
                await ctx.send(f'Бот уже занят:( Он находится в канале **{ctx.voice_client.channel.name}**')
                return
            vc = ctx.voice_client
        else:
            vc = await ctx.author.voice.channel.connect()

        id = ctx.author.guild.id
        if id not in self.queue:
            self.queue[id] = MusicQueue()

        msg = await ctx.send(f'Попытка добавления трека...')

        video = self.queue[id].add_music(link_or_query)
        if video['ok'] == False or video['length'] < 1:
            await msg.edit(content=f"Не удалось добавить трек")
        if video['type'] == "playlist":
            await msg.edit(content=f"Плейлист добавлен в очередь, количество добавленных треков: {video['length']}")
        elif video['type'] == "video":
            await msg.edit(content=f'Трек добавлен в очередь')
        else:
            await msg.edit(content=f"Не удалось добавить трек")

        if vc.is_playing() or vc.is_paused():
            return

        for current_music in self.queue[id]:
            vc.play(discord.FFmpegPCMAudio(
                source=current_music.direct_url, before_options=ffmpeg_options['before_options'], options=ffmpeg_options['options']))
            await ctx.channel.send(f"Сейчас проигрывается: `{current_music.title}` от **{current_music.author}** [`{current_music.getReadableTime()}`]")
            # vc.source = discord.PCMVolumeTransformer(vc.source, volume=1.0)

            while vc.is_playing() or vc.is_paused():
                await asyncio.sleep(1)

    @commands.hybrid_command()
    async def skip(self, ctx: commands.Context):
        """Пропускает текущий трек в очереди, если возможно"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно пропустить трек не находясь в канале: {ctx.voice_client.channel.name}')
            return
        if not helpers.queue_is_empty(ctx, self.queue):
            ctx.voice_client.stop()
            await ctx.send(f'Пропустил трек')
            return

        await ctx.send(f'Очередь уже пуста')

    @commands.hybrid_command()
    async def pause(self, ctx: commands.Context):
        """Ставит трек на паузу"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно пропустить трек не находясь в канале: {ctx.voice_client.channel.name}')
            return
        if not helpers.queue_is_empty(ctx, self.queue):
            ctx.voice_client.pause()
            await ctx.send(f'Поставил на паузу')
            return

        await ctx.send(f'Очередь пуста')

    @commands.hybrid_command()
    async def resume(self, ctx: commands.Context):
        """Возобновляет воспроизведение трека"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно пропустить трек не находясь в канале: {ctx.voice_client.channel.name}')
            return
        if not helpers.queue_is_empty(ctx, self.queue):
            ctx.voice_client.resume()
            await ctx.send(f'Возобновил воспроизведение')
            return

        await ctx.send(f'Очередь пуста')

    @commands.hybrid_command()
    async def stop(self, ctx: commands.Context):
        """Останавливает проигрывание и очищает очередь"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно остановить бота не находясь в канале: {ctx.author.voice.channel.name}')
            return
        if not helpers.queue_is_empty(ctx, self.queue):
            id = ctx.author.guild.id
            if id in self.queue:
                self.queue[id].remove_queue()
            ctx.voice_client.stop()
            await ctx.send(f'Очередь очищена')
            return

        await ctx.send(f'Очередь уже пуста')

    @commands.hybrid_command()
    async def disconnect(self, ctx: commands.Context):
        """Отключает бота от канала"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно отключить бота не находясь в канале: {ctx.author.voice.channel.name}')
            return
        if not helpers.queue_is_empty(ctx, self.queue):
            self.queue[ctx.author.guild.id].remove_queue()
        if helpers.bot_is_playing(ctx):
            ctx.voice_client.stop()

        await ctx.voice_client.disconnect()
        await ctx.send(f'Бот отключен')

    @commands.hybrid_command()
    async def shuffle(self, ctx: commands.Context):
        """Перемешивает оставшуюся очередь"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно взаимодействовать с ботом не находясь в канале: {ctx.author.voice.channel.name}')
            return
        if not helpers.queue_is_empty(ctx, self.queue):
            random.shuffle(self.queue[ctx.author.guild.id].queue)
            await ctx.send(f'Очередь перемешана')
            return

        await ctx.send(f'Очередь пуста')

    @commands.hybrid_command()
    async def now_playing(self, ctx: commands.Context):
        """Отображает текущую проигрываемую музыку"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно взаимодействовать с ботом не находясь в канале: {ctx.author.voice.channel.name}')
            return
        video = self.queue[ctx.author.guild.id].now_playing
        if video:
            await ctx.send(f'Сейчас проигрывается: {video.url}')
            return

        await ctx.send(f'Сейчас ничего не проигрывается')

    @commands.hybrid_command()
    async def list(self, ctx: commands.Context, page=1):
        """Отображает первые 20 треков в очереди с n-страницы"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно взаимодействовать с ботом не находясь в канале: {ctx.author.voice.channel.name}')
            return
        if helpers.queue_is_empty(ctx, self.queue):
            await ctx.send(f'Очередь пуста')
            return

        length = self.queue[ctx.author.guild.id].length()

        maxpage = math.ceil(length / 20)
        if page > maxpage:
            page = maxpage
        elif page < 1:
            page = 1

        start = (page-1) * 20
        end = page * 20
        end = length if end > length else end

        temp = ""
        for i in range(start, end):
            video = self.queue[ctx.author.guild.id].queue[i]
            temp += f'`{i+1}`. **{video.title}** [`{video.getReadableTime()}`]\n'

        await ctx.send(f'Количество треков в очереди: {length}\n\n{temp}\nСтраница: {page} / {maxpage}')


@tasks.loop(minutes=10)
async def change_activity():
    status = random.choice(
        ["кушает картошку", "завис(шутка)", "наелся и спит"])

    print(status)
    await bot.change_presence(activity=discord.Game(name=status))


@bot.event
async def on_ready():
    await bot.add_cog(customCommand(bot))
    await bot.tree.sync()
    await change_activity.start()

load_dotenv()

token = os.getenv('BOT_TOKEN')

bot.run(token)
