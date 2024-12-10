import os
import discord
import pytz
from discord.ext import commands
from discord.utils import utcnow
from datetime import timedelta
from dotenv import load_dotenv
import constants as id

load_dotenv()

token = os.environ.get("NOTBANI")
intents = discord.Intents.none()
intents.guilds = True
intents.guild_scheduled_events = True

utc = pytz.utc
est = pytz.timezone("US/Eastern")

bot = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)

@bot.event
async def on_ready():
    print("Logged in")
    guild = bot.get_guild(id.Server.BANIVERSE)
    events = guild.scheduled_events

    for event in events:
        utc_start_time = event.start_time.replace(tzinfo=utc)
        est_start_time = utc_start_time.astimezone(est)
        print(f"- {event.name}: {est_start_time.strftime('%A, %I %p')} (EST) - {event.id}")

    # skip = [1293345320180125766,
    #         1301278823232573503,
    #         1301279070549446790,
    #         1301279216150511626,
    #         1301279363358130287,
    #         1313301203823759400]

    # for event in events:
    #     if event.id not in (skip):
    #         new_start_time = event.start_time + timedelta(hours=1)
    #         new_end_time = new_start_time + timedelta(hours=1)

    #         await event.edit(
    #             start_time=new_start_time,
    #             end_time=new_end_time
    #         )
    print("Done")

bot.run(token)