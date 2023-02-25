from discord.ext import commands

from application.bot import Bot
from application.commands import AppCommand
from application.context import AppContext


class StopCommand(AppCommand):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def stop(self, ctx: AppContext):
        """
        Stops the song and cleans queue
        """

        if not ctx.is_client_connected():
            await ctx.send(f'Бот не подключен')
            return
        if not ctx.is_same_channel():
            await ctx.send(f'Невозможно остановить бота не находясь в канале: {ctx.author.voice.channel.name}')
            return
        if ctx.is_client_playing():
            id = ctx.author.guild.id
            if id in self.bot.queueMap:
                self.bot.queueMap[id].clean()
            ctx.voice_client.stop()
            await ctx.send(f'Очередь очищена')
            return
        await ctx.send(f'В данный момент ничего не проигрывается')
