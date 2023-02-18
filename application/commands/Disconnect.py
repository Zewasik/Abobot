from discord.ext import commands

from application.bot import Bot
from application.commands import AppCommand
from application.context import AppContext


class DisconnectCommand(AppCommand):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def disconnect(self, ctx: AppContext):
        """Disconnects bot from the channel"""

        if not ctx.is_client_connected():
            await ctx.send(f'Бот не подключен')
            return
        if not ctx.is_same_channel():
            await ctx.send(f'Невозможно отключить бота не находясь в канале: {ctx.author.voice.channel.name}')
            return
        if ctx.is_client_playing():
            self.bot.queueMap[ctx.author.guild.id].clean()
            ctx.voice_client.stop()

        await ctx.voice_client.disconnect()
        await ctx.send(f'Бот отключен')


    