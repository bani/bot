import os
import discord
import time
from datetime import time
import pytz as tz
from dotenv import load_dotenv
from discord.ext import tasks
import constants as id
import calendar_parser


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
time = time(hour=17, minute=30, tzinfo=tz.timezone('America/Toronto'))

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    if not calendar.is_running():
        calendar.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # handle DMs
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id != id.User.BANI:
            print(f"{message.author.name}: {message.content}")

# @tasks.loop(minutes=2)
@tasks.loop(time=time)
async def calendar():
    try:
        events = calendar_parser.get_events()

        if len(events) > 0:
            embed=discord.Embed(color=0x7209B7)
            embed.set_author(name="TwT", url="https://www.tripp.com/events/", icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSAzHb8Hu_YT4pQTZu2-DvWlaFqjVzAP_xLYDCFlFF72A&s")
            for event in events:
                embed.add_field(name=event[2], value=f"<t:{event[0]}:t> {event[1]}", inline=False)

            await client.get_channel(id.Channel.TMP).send(embed=embed)
        else:
            await client.get_channel(id.Channel.TMP).send(f"No events found.")

    except Exception as e:
        print(e)

load_dotenv()
client.run(os.environ.get("DISCORD_TOKEN"))
