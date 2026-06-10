import os
import re
import discord
import traceback
from dotenv import load_dotenv
import constants as id

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

msg_asoka = "The Artificial Buddha with <#1469030252402708654> has concluded. New events coming in June."

params = {
    'bot': 'CALENDAR', # 'CALENDAR'
    'channel': id.Channel.ALTCAL, #ALTCAL
    'message': msg_asoka
}

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    await message()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # handle DMs
    if isinstance(message.channel, discord.DMChannel):
        print(f"{message.author.name}: {message.content}")

async def message():
    try:

        embed=discord.Embed(color=0xFFC107, title="")
        # embed.set_thumbnail(url="https://www.emoji.family/api/emojis/1f514/noto/png/128")
        embed.set_author(name=f"Event Update", url="", icon_url="https://www.emoji.family/api/emojis/1f514/noto/png/128")
        embed.add_field(name="", value=f"{params['message']}", inline=False)

        await client.get_channel(params['channel']).send(embed=embed)

        print("Done")

    except Exception as e:
        print(traceback.format_exc())

load_dotenv()
client.run(os.environ.get(params['bot']))
