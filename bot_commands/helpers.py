from discord.ext import commands


def bot_is_connected(ctx: commands.Context):
    return ctx.voice_client != None


def author_is_connected(ctx: commands.Context):
    return ctx.author.voice and ctx.author.voice.channel


def is_same_channel(ctx: commands.Context):
    return author_is_connected(ctx) and ctx.voice_client.channel == ctx.author.voice.channel


def bot_is_playing(ctx: commands.Context) -> bool:
    return bot_is_connected(ctx) and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused())


def queue_is_empty(ctx: commands.Context, queue):
    id = ctx.author.guild.id

    return id not in queue or queue[id].is_empty()
