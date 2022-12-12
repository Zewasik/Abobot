import os
from discord.ext import commands, tasks
import discord
import random
from dotenv import load_dotenv

from bot_commands import Disconnect, List, NowPlaying, Pause, Play, Resume, Shuffle, Skip, Stop
from bot_commands.bot_wrapper import BotWrapper


def main():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = BotWrapper(
        command_prefix=commands.when_mentioned_or("!"), intents=intents, description="ну он музыку короче играет")

    load_dotenv()
    TOKEN = os.getenv('BOT_TOKEN')

    if not TOKEN:
        print("Отсутствует .env файл с токеном")
        exit(1)

    @tasks.loop(minutes=10)
    async def change_activity():
        status = random.choice(
            ["кушает картошку", "завис(шутка)", "наелся и спит", "Dota 2"])

        print(status)
        await bot.change_presence(activity=discord.Game(name=status))

    @bot.event
    async def on_ready():
        await bot.add_cog(Disconnect.DisconnectCommand(bot))
        await bot.add_cog(List.ListCommand(bot))
        await bot.add_cog(NowPlaying.NowPlayingCommand(bot))
        await bot.add_cog(Pause.PauseCommand(bot))
        await bot.add_cog(Play.PlayCommand(bot))
        await bot.add_cog(Resume.ResumeCommand(bot))
        await bot.add_cog(Shuffle.ShuffleCommand(bot))
        await bot.add_cog(Skip.SkipCommand(bot))
        await bot.add_cog(Stop.StopCommand(bot))

        await bot.tree.sync()
        await change_activity.start()

    bot.run(TOKEN)


if __name__ == '__main__':
    main()
