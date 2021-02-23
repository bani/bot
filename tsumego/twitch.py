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

    m = re.search(r'^([a-tA-T]{1})([0-9]{1,2})$', ctx.content)
    if m:
      result = tsumego.place_stone(m.group(1), m.group(2), ctx.author.name)
      await ctx.channel.send(result)


@bot.command(name='help')
async def help(ctx):
    await ctx.send("Enter the coordinates where you'd like to play in the chat (e.g. A1). If you need to enter the same coordinate twice in a row, you can switch between upper and lower case. Other available commands: !link: URL for current problem; !review: URL of last problem; !rank change the rank of the next problem.")

@bot.command(name='review')
async def review(ctx):
    await ctx.send(tsumego.url)

@bot.command(name='link')
async def link(ctx):
    await ctx.send(tsumego.driver.current_url)

@bot.command(name='rank')
async def rank(ctx):
    msg = ctx.message.clean_content
    m = re.search(r'rank (.+)', msg)
    if m:
        if tsumego.update_rank(m.group(1)):
            await ctx.send('Rank updated, it\'ll be used on next problem.')
        else:
            await ctx.send('Invalid rank. Use 5d to 20k. E.g. !rank 10k')


if __name__ == "__main__":
    tsumego = tsumego.Tsumego()
    bot.run()

