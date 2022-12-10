from discord.ext import commands
from bot_commands.bot_wrapper import BotWrapper
import bot_commands.helpers as helpers

class StopCommand(commands.Cog):
    def __init__(self, bot: BotWrapper):
        self.bot = bot

    @commands.hybrid_command()
    async def stop(self, ctx: commands.Context):
        """Останавливает проигрывание и очищает очередь"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно остановить бота не находясь в канале: {ctx.author.voice.channel.name}')
            return
        if helpers.bot_is_playing(ctx):
            id = ctx.author.guild.id
            if id in self.bot.queue:
                self.bot.queue[id].remove_queue()
            ctx.voice_client.stop()
            await ctx.send(f'Очередь очищена')
            return

        await ctx.send(f'В данный момент ничего не проигрывается')
