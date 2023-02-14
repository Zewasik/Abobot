import time
from discord.ext import commands
from bot_commands.bot_wrapper import BotWrapper
import bot_commands.helpers as helpers


class NowPlayingCommand(commands.Cog):
    def __init__(self, bot: BotWrapper):
        self.bot = bot

    @commands.hybrid_command()
    async def now_playing(self, ctx: commands.Context):
        """Отображает текущую проигрываемую музыку"""

        if not helpers.bot_is_connected(ctx):
            await ctx.send(f'Бот не подключен')
            return
        if not helpers.is_same_channel(ctx):
            await ctx.send(f'Невозможно взаимодействовать с ботом не находясь в канале: {ctx.author.voice.channel.name}')
            return
        video = self.bot.queue[ctx.author.guild.id].now_playing
        if video:
            # temp = f'`|{"-"*timeParts}>{"_"*(20-timeParts)}|`'
            temp = f'`{video.get_readable_time(int(time.time() - video.start_time))}`/`{video.get_readable_time()}`'
            await ctx.send(f'Сейчас проигрывается: {video.url}. Оставшееся время: {temp}')
            return

        await ctx.send(f'Сейчас ничего не проигрывается')
