from discord.ext import commands
from bot_commands.bot_wrapper import BotWrapper
import bot_commands.helpers as helpers


class PauseCommand(commands.Cog):
    def __init__(self, bot: BotWrapper):
        self.bot = bot

    @commands.hybrid_command()
    async def pause(self, ctx: commands.Context):
        """Ставит трек на паузу"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно пропустить трек не находясь в канале: {ctx.voice_client.channel.name}')
            return
        if helpers.bot_is_playing(ctx):
            ctx.voice_client.pause()
            await ctx.send(f'Поставил на паузу')
            return

        await ctx.send(f'В данный момент ничего не проигрывается')
    