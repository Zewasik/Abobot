from pytube import YouTube
from sqlite3 import connect
from discord.ext import commands
import discord

KEY = '$play '

# Download from youtube


async def download_from_youtube(urlToDownload):
    print('downloading...')
    yt = YouTube(urlToDownload)
    name = yt.streams.filter(
        only_audio=True, mime_type="audio/webm").first().download()
    # audio_file = open(name, "r+b").read()

    return name

# Discord part

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"), intents=intents)


class customCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def play(self, ctx: commands.Context, youtube_link):
        music_path = await download_from_youtube(youtube_link)
        # vc = await ctx.author.voice.channel.connect()
        print(ctx.voice_client)

        vc = [vc for vc in bot.voice_clients if vc == ctx.voice_client]
        vc = vc[0] if len(vc) > 0 else await ctx.author.voice.channel.connect()

        print(ctx.voice_client)
        print([vc for vc in bot.voice_clients if vc == ctx.voice_client])
        # print(ctx.author.voice)
        vc.play(discord.FFmpegPCMAudio(
            executable="ffmpeg", source=music_path))
        vc.source = discord.PCMVolumeTransformer(vc.source, volume=1.0)
        await ctx.send("Пацаны, добавил в очередь эту песню кароче: " + youtube_link)


@bot.event
async def on_ready():
    await bot.add_cog(customCommand(bot))
    await bot.tree.sync()
    print("Started")

bot.run(
    'MTAzMzY3NjY3MzM0MzgyMzkwNA.Gh06Dm.IKcYJpyNw-9DwgwbLB-_UFQFJ7GCx-YB38WN8w')
