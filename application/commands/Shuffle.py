from discord.ext import commands

from application.bot import Bot
from application.commands import AppCommand
from application.context import AppContext


class ShuffleCommand(AppCommand):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def shuffle(self, ctx: AppContext):
        """
        Shuffles left queue
        """

        if not ctx.is_client_connected():
            await ctx.send(f'Бот не подключен')
            return
        if not ctx.is_same_channel():
            await ctx.send(f'Невозможно взаимодействовать с ботом не находясь в канале: '
                           f'{ctx.author.voice.channel.name}')
            return
        if not self.bot.queue_is_empty(ctx.author.guild.id):
            self.bot.queueMap[ctx.author.guild.id].shuffle()
            await ctx.send(f'Очередь перемешана')
            return

        await ctx.send(f'Очередь пуста')
