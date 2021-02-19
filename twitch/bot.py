# bot.py
import os # for importing env vars for the bot to use
from twitchio.ext import commands

import os
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL']]
)

@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{os.environ['BOT_NICK']} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"/me is here!")

@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'

    # make sure the bot ignores itself and the streamer
    if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
        return

    await bot.handle_commands(ctx)

    print(f"{ctx.author.name}: {ctx.content}")

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('pong!')

@bot.command(name='ogs')
async def ogs(ctx):
    await ctx.send('https://online-go.com/player/920382/')

if __name__ == "__main__":
    bot.run()
