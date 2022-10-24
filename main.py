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


@bot.event
async def on_ready():
    print("Started")


@bot.command()
async def play(ctx, link):
    print(link)
    music_for_men = await download_from_youtube(link)
    vc = await ctx.author.voice.channel.connect()
    vc.play(discord.FFmpegPCMAudio(
        executable="ffmpeg", source=music_for_men))
    vc.source = discord.PCMVolumeTransformer(vc.source, volume=0.5)

bot.run(
    'MTAzMzY3NjY3MzM0MzgyMzkwNA.Gh06Dm.IKcYJpyNw-9DwgwbLB-_UFQFJ7GCx-YB38WN8w')
