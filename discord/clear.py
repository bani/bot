"""Persistent bot exposing a /clear slash command in BANIVERSE that purges
the invoking channel's unpinned messages older than a week."""

import argparse
import asyncio
import logging
from datetime import timedelta

import discord
from discord import app_commands
from discord.utils import utcnow

import bot_common
from constants import Server

log = logging.getLogger("bot.clear")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bot", default="DISCORD_TOKEN",
                        help="env var holding the bot token (default: %(default)s)")
    return parser.parse_args()


def main():
    args = parse_args()
    client = bot_common.make_client()
    tree = app_commands.CommandTree(client)
    guild = discord.Object(id=Server.BANIVERSE)

    @client.event
    async def on_ready():
        log.info("Logged in as %s", client.user)
        await tree.sync(guild=guild)
        log.info("Ready!")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if bot_common.is_dm(message):
            bot_common.log_dm(message)

    @tree.command(name="clear", description="Clear channel's old history", guild=guild)
    async def clear_command(interaction):
        await interaction.response.defer(ephemeral=True)

        cutoff = utcnow() - timedelta(days=7)
        async for message in interaction.channel.history(before=cutoff):
            if not message.pinned:
                await message.delete()
                await asyncio.sleep(1)

        await interaction.followup.send("Cleared!")

    bot_common.run(client, args.bot)


if __name__ == "__main__":
    main()
