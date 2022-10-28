import asyncio
from pytube import YouTube, Search
from sqlite3 import connect
from discord.ext import commands
import discord
import re

KEY = '$play '

ffmpeg_options = {
    'options': '-bufsize 6000k',
}


def get_direct_url(urlToSearch: str) -> str:
    try:
        return YouTube(urlToSearch).streams.get_by_itag(251).url
    except Exception as e:
        print(e)
        return None


def search_by_query(query: str) -> str:
    s = Search(query)
    s.results[0]

    return


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"), intents=intents)


class customCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.music_queue = dict()

    @commands.hybrid_command()
    async def play(self, ctx: commands.Context, link_or_query):
        vc = [vc for vc in bot.voice_clients if vc == ctx.voice_client]
        vc = vc[0] if len(vc) > 0 else await ctx.author.voice.channel.connect()

        id = ctx.author.guild.id
        if id in self.music_queue:
            self.music_queue[id].append(link_or_query)
        else:
            self.music_queue[id] = list([link_or_query])

        await ctx.send("Пацаны, добавил в очередь эту песню кароче: " + link_or_query)

        print(self.music_queue)
        if not vc.is_playing():
            while True:
                if not vc.is_playing() and len(self.music_queue[id]) > 0:
                    print("закончил играть")
                    current_music = self.music_queue[id].pop(0)
                    m = re.search(
                        "(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?", current_music)

                    if m == None:
                        # await ctx.send("Брат, ссылку введи нормально")
                        current_music = search_by_query(current_music)
                    else:
                        current_music = m.group(0)
                        current_music = get_direct_url(current_music)
                    vc.play(discord.FFmpegPCMAudio(
                        executable="ffmpeg", source=current_music, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"), after=lambda e: print("Music played"))
                    # vc.source = discord.PCMVolumeTransformer(vc.source, volume=1.0)
                if not vc.is_playing() and len(self.music_queue[id]) <= 0:
                    await ctx.send(content="Очередь закончилась, я ухожу:(", reference=None)
                    await vc.disconnect()
                    break

                await asyncio.sleep(5)

        return


@bot.event
async def on_ready():
    await bot.add_cog(customCommand(bot))
    await bot.tree.sync()
    print("Started")

bot.run(
    'MTAzMzY3NjY3MzM0MzgyMzkwNA.Gh06Dm.IKcYJpyNw-9DwgwbLB-_UFQFJ7GCx-YB38WN8w')
