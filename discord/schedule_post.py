import os
import discord
import re
# import time
import traceback
from datetime import time
import pytz as tz
from dotenv import load_dotenv
from discord.ext import tasks
import constants as id
import calendar_parser


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
# time = time(hour=21, minute=15, tzinfo=tz.timezone('America/Toronto'))
params = {
    'post': True,
    'channel': id.Channel.TMP,
    'offset': 0
}

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    if not calendar.is_running():
        if params['post']:
            calendar.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # handle DMs
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id == id.User.BANI:
            if message.content.startswith('$del'):
                await delete(message)
    else:
            print(f"{message.author.name}: {message.content}")

@tasks.loop(hours=24)
# @tasks.loop(time=time)
async def calendar():
    try:
        calendar_url = os.environ.get("CALENDAR_URL")
        events, events_date = calendar_parser.get_events(calendar_url=calendar_url, offset=params['offset'])

        if len(events) > 0:
            embed=discord.Embed(color=0xFF7D7D)
            embed.set_author(name=f"{events_date}", url="", icon_url="https://cdn.discordapp.com/attachments/1291477863811514522/1293693113822478420/F2445A85-BB7E-4357-A488-D0500DB4DEF1.webp?ex=67103619&is=670ee499&hm=4a5486baa19226e0f147416327010bebd00acb919f488af85477fb0e794e618b&")
            for event in events:
                embed.add_field(name="\u200B\n"+event[1], value=f"Time: <t:{event[0]}:t>", inline=False)

            await client.get_channel(params['channel']).send(embed=embed)
        else:
            await client.get_channel(params['channel']).send(f"No events found on {events_date}.")

    except Exception as e:
        print(traceback.format_exc())

async def delete(message):
    try:
        match = re.compile('\$del ([A-Z]+) (.*)').search(message.content)
        channel = client.get_channel(getattr(id.Channel, match[1]))
        msg = await channel.fetch_message(int(match[2]))
        await msg.delete()
    except Exception as e:
        print(message.content)
        print(e)

load_dotenv()
client.run(os.environ.get("CALENDAR"))
