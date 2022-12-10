import random
from discord.ext import commands
from bot_commands.bot_wrapper import BotWrapper
import bot_commands.helpers as helpers


class ShuffleCommand(commands.Cog):
    def __init__(self, bot: BotWrapper):
        self.bot = bot

    @commands.hybrid_command()
    async def shuffle(self, ctx: commands.Context):
        """Перемешивает оставшуюся очередь"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно взаимодействовать с ботом не находясь в канале: {ctx.author.voice.channel.name}')
            return
        if not helpers.queue_is_empty(ctx, self.bot.queue):
            random.shuffle(self.bot.queue[ctx.author.guild.id].queue)
            await ctx.send(f'Очередь перемешана')
            return

        await ctx.send(f'Очередь пуста')
