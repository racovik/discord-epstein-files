import discord
from discord.ext import commands

import logging

import os
from dotenv import load_dotenv

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("epstein_bot")

description = """A bot that permit users search on the epstein files.

"""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="?", description=description, intents=intents)


async def load_cogs():
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            cog_name = file[:-3]
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                logger.info(f"Cog loaded: {cog_name}")
            except Exception as e:
                logger.error(f"Error loading cog {cog_name}: {e}")


async def sync_commands():
    try:
        synced = await bot.tree.sync()
        logger.info(f"slash commands synced: {len(synced)}")
        return synced
    except discord.errors.HTTPException as e:
        logger.error(f"Error syncing slash commands: {e}")
        return []


@bot.event
async def on_ready():
    # Tell the type checker that User is filled up at this point
    assert bot.user is not None
    await load_cogs()
    await sync_commands()

    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")


bot.run(discord_token)
