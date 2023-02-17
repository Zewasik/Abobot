from discord.ext import commands

from application.bot import Bot
from application.commands import AppCommand
from application.context import AppContext


class ResumeCommand(AppCommand):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def resume(self, ctx: AppContext):
        """
        Continues paused song
        """

        if not ctx.is_client_connected():
            await ctx.send(f'Бот не подключен')
            return
        if not ctx.is_same_channel():
            await ctx.send(f'Невозможно пропустить трек не находясь в канале: {ctx.voice_client.channel.name}')
            return
        if ctx.is_client_playing():
            ctx.voice_client.resume()
            await ctx.send(f'Возобновил воспроизведение')
            return

        await ctx.send(f'В данный момент ничего не проигрывается')
    