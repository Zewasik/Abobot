import os
from pytube import YouTube
from sqlite3 import connect
import discord

KEY = '$play '

# Download from youtube


async def download_from_youtube(urlToDownload):
    print('downloading...')
    yt = YouTube(urlToDownload)
    name = yt.streams.filter(
        only_audio=True, mime_type="audio/webm").first().download('.')
    # audio_file = open(name, "r+b").read()

    return name

# Discord part

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'Ready')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(KEY):
        music_for_men = await download_from_youtube(
            'https://www.youtube.com/watch?v=lOPSaf9bFQ4&list=RDQkNA98LJ6ko&index=3&ab_channel=CrazyCater41')
        vc = await message.author.voice.channel.connect()
        vc.play(discord.FFmpegPCMAudio(
            executable="/usr/bin/ffmpeg", source=music_for_men))
        vc.source = discord.PCMVolumeTransformer(vc.source, volume=0.02)


client.run(
    'MTAzMzY3NjY3MzM0MzgyMzkwNA.Gh06Dm.IKcYJpyNw-9DwgwbLB-_UFQFJ7GCx-YB38WN8w')
