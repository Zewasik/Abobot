import os
import random

import json

import config
from config import Configuration
import dacite as dacite

from discord.ext import commands, tasks
from discord import Intents, Game

from bot_commands import Disconnect, List, NowPlaying, Pause, Play, Resume, Shuffle, Skip, Stop
from bot_commands.bot_wrapper import BotWrapper


intents = Intents.default()
intents.message_content = True

bot = BotWrapper(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents,
    description="ну он музыку короче играет")


@tasks.loop(minutes=10)
async def change_activity():
    status = random.choice(
        ["кушает картошку", "завис(шутка)", "наелся и спит", "Dota 2"])

    print(status)
    await bot.change_presence(activity=Game(name=status))


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

if __name__ == '__main__':
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        print(f"Отсутствует переменная окружения BOT_TOKEN")
        exit(1)

    JSON_CONFIG_PATH = os.getenv('JSON_CONFIG_PATH')
    if not JSON_CONFIG_PATH:
        print(f"Отсутствует переменная окружения JSON_CONFIG_PATH")
        exit(1)

    with open(os.getenv('JSON_CONFIG_PATH'), "r") as f:
        raw_config = json.load(f)

    config.CONFIG = dacite.from_dict(
        data_class=Configuration, data=raw_config
    )
    bot.run(TOKEN)
