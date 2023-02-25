import logging
import os
import random
import json

import dacite
from dotenv import load_dotenv

from discord.ext import commands, tasks
from discord import Intents, Game

import config
from config import Configuration
from application.bot import Bot
import application.commands as app_commands
from application.util import ApiSelector


intents = Intents.default()
intents.message_content = True

bot = Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents,
    description="ну он музыку короче играет")

logFormatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)
logger.addHandler(consoleHandler)


@tasks.loop(minutes=10)
async def change_activity():
    """
    :D
    """
    status = random.choice(
        ["кушает картошку", "завис(шутка)", "наелся и спит", "Dota 2"])

    print(status)
    await bot.change_presence(activity=Game(name=status))


@bot.event
async def on_ready():
    """
    Finds all AppCommands and attaches them to bot
    """
    for cls in app_commands.AppCommand.__subclasses__():
        await bot.add_cog(cls(bot))
    await bot.tree.sync()
    await change_activity.start()


if __name__ == '__main__':
    logger.info("Reading .env")
    load_dotenv()

    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        logger.critical("BOT_TOKEN parameter was not provided")
        exit(1)

    JSON_CONFIG_PATH = os.getenv('JSON_CONFIG_PATH')
    if not JSON_CONFIG_PATH:
        logger.critical("JSON_CONFIG_PATH parameter was not provided")
        exit(1)

    with open(os.getenv('JSON_CONFIG_PATH'), "r") as f:
        raw_config = json.load(f)

    config.CONFIG = dacite.from_dict(
        data_class=Configuration, data=raw_config
    )
    ApiSelector()
    logger.info("Starting up the bot!")
    bot.run(TOKEN)
