from discord.ext import commands
from bot_commands.bot_wrapper import BotWrapper
import bot_commands.helpers as helpers

class ResumeCommand(commands.Cog):
    def __init__(self, bot: BotWrapper):
        self.bot = bot

    @commands.hybrid_command()
    async def resume(self, ctx: commands.Context):
        """Возобновляет воспроизведение трека"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно пропустить трек не находясь в канале: {ctx.voice_client.channel.name}')
            return
        if not helpers.queue_is_empty(ctx, self.bot.queue):
            ctx.voice_client.resume()
            await ctx.send(f'Возобновил воспроизведение')
            return

        await ctx.send(f'Очередь пуста')
    