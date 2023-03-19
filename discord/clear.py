import os
import discord
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import constants as id
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    await tree.sync(guild=discord.Object(id=id.Server.BANIVERSE))
    print("Ready!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # handle DMs
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id != id.User.BANI:
            print(f"{message.author.name}: {message.content}")

@tree.command(name = "clear", description = "Clear channel's old history", guild=discord.Object(id=id.Server.BANIVERSE))
async def clear_command(interaction):
    await interaction.response.defer(ephemeral=True)

    old = datetime.now() - timedelta(30)

    async for message in interaction.channel.history(before=old):
        if not message.pinned:
            await message.delete()
            time.sleep(1)

    await interaction.followup.send("Cleared!")

load_dotenv()
client.run(os.environ.get("DISCORD_TOKEN"))
