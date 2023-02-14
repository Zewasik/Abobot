from discord.ext import commands
from bot_commands.bot_wrapper import BotWrapper
import bot_commands.helpers as helpers


class DisconnectCommand(commands.Cog):
    def __init__(self, bot: BotWrapper):
        self.bot = bot

    @commands.hybrid_command()
    async def disconnect(self, ctx: commands.Context):
        """Отключает бота от канала"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно отключить бота не находясь в канале: {ctx.author.voice.channel.name}')
            return
        if helpers.bot_is_playing(ctx):
            self.bot.queue[ctx.author.guild.id].remove_queue()
            ctx.voice_client.stop()

        await ctx.voice_client.disconnect()
        await ctx.send(f'Бот отключен')


    