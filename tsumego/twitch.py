import os
import re
from twitchio.ext import commands
from dotenv import load_dotenv
import tsumego

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
    # await ws.send_privmsg(os.environ['CHANNEL'], f"/me is here!")

@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'

    # make sure the bot ignores itself and the streamer
    if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
        return

    await bot.handle_commands(ctx)

    m = re.search(r'(^[a-iA-I]{1})([0-9]{1})$', ctx.content)
    if m:
      result = tsumego.place_stone(m.group(1), m.group(2), ctx.author.name)
      await ctx.channel.send(result)

    # print(f"{ctx.author.name}: {ctx.content}")

@bot.command(name='play')
async def play(ctx):
    msg = ctx.message.clean_content
    m = re.search(r'play ([a-iA-i]{1})([0-9]{1})', msg)
    if m:
      result = tsumego.place_stone(m.group(1), m.group(2), ctx.message.author.name)
      await ctx.send(result)

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('pong!')

@bot.command(name='ogs')
async def ogs(ctx):
    await ctx.send('https://online-go.com/player/920382/')


if __name__ == "__main__":
    tsumego = tsumego.Tsumego()
    bot.run()

