import os
import discord
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import constants as id

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    print("Ready!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # handle DMs
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id != id.User.BANI:
            print(f"{message.author.name}: {message.content}")


        if message.author.id == id.User.BANI:
            if message.content.startswith('$clear'):
                await clear_old()


async def clear_old():

    old = datetime.now() - timedelta(1)

    async for message in client.get_channel(id.Channel.BIRTH).history(before=old):
        if not message.pinned and message.author.id == id.User.BIRTH:
            # await message.delete()
            print(f"> TO BE DELETED: {message.author.id} {message.content}")
            time.sleep(1)

load_dotenv()
client.run(os.environ.get("CALENDAR"))
