"""Persistent bot that answers messages in the TMP channel via OpenAI,
with a /clear slash command to wipe the channel's recent history."""

import argparse
import asyncio
import logging
import os
from datetime import timedelta

import discord
from discord import app_commands
from discord.utils import utcnow
from openai import AsyncOpenAI

import bot_common
from constants import Channel, Server

log = logging.getLogger("bot.chatgpt")

SCIENCE_PROMPT = """You are a knowledgeable Philosopher who enjoys discussing science, metaphysics, the nature of reality and the universe.
Your responses should be concise and grounded on research from published papers. Provide references.
"""

MINDFULNESS_PROMPT = """You are a wise mindfulness guide aiming to improve your user's mental health through a practice of focusing on the present moment, positive thinking and gratitude.
You don't follow a specific religion, but your knowledge is grounded on principles of Buddhism and Stoicism.
Your answers should be concise and include quotes from influential Philosophers, Thinkers, Meditation authors, or leaders, always providing attribution.
Avoid being repetitive. Refuse to talk about illegal substances or psychedelics.
"""

SYSTEM_PROMPT = SCIENCE_PROMPT


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bot", default="DISCORD_TOKEN",
                        help="env var holding the bot token (default: %(default)s)")
    parser.add_argument("--model", default="gpt-3.5-turbo",
                        help="OpenAI model (default: %(default)s)")
    return parser.parse_args()


def main():
    args = parse_args()
    bot_common.setup_logging()
    token = bot_common.get_token(args.bot)  # also loads .env for the OpenAI key
    openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAPI"))

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

        if message.channel.id == Channel.TMP:
            await respond(message)

    async def respond(message):
        log.info("### %s: %s", message.author.name, message.content)

        cutoff = utcnow() - timedelta(days=1)
        history = []
        async for msg in message.channel.history(after=cutoff, oldest_first=False, limit=3):
            history.append({
                "role": "assistant" if msg.author == client.user else "user",
                "content": msg.content})
        history.append({"role": "system", "content": SYSTEM_PROMPT})
        history.reverse()

        response = await openai_client.chat.completions.create(
            model=args.model,
            messages=history,
        )
        choice = response.choices[0]
        log.info("Reply: reason: %s, tokens: %s",
                 choice.finish_reason, response.usage.total_tokens)
        reply = choice.message.content

        moderation = await openai_client.moderations.create(input=reply)
        if moderation.results[0].flagged:
            log.warning("Reply flagged by moderation: %s", moderation)
            reply = "Sorry, I can't help with that."

        await message.channel.send(reply)

    @tree.command(name="clear", description="Clear channel's recent history", guild=guild)
    async def clear_command(interaction):
        if interaction.channel_id != Channel.TMP:
            await interaction.response.send_message("Command not available on this channel!")
            return

        await interaction.response.defer(ephemeral=True)
        cutoff = utcnow() - timedelta(days=1)
        async for message in interaction.channel.history(after=cutoff):
            await message.delete()
            await asyncio.sleep(1)
        await interaction.followup.send("Cleared!")

    client.run(token, log_handler=None)


if __name__ == "__main__":
    main()
