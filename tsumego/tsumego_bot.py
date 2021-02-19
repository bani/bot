# bot.py
import os # for importing env vars for the bot to use
import re
from twitchio.ext import commands

import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

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

    # print(f"{ctx.author.name}: {ctx.content}")

@bot.command(name='play')
async def ping(ctx):
    msg = ctx.message.clean_content
    m = re.search(r'play ([a-z]{2})', msg)
    place_stone(m.group(1))
    await ctx.send('tap')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('pong!')

@bot.command(name='ogs')
async def ogs(ctx):
    await ctx.send('https://online-go.com/player/920382/')

def fancy_click(id):
    driver.execute_script("arguments[0].click();", driver.find_element_by_id(id))

def solution_check():
    solution_check = driver.find_element_by_id('solutionContainer')
    if solution_check.text == 'Completed!':
        fancy_click('loadButton')
    elif solution_check.text == 'Wrong. Keep trying.':
        driver.execute_script("stepBeginning()")

def place_stone(coords):
    fancy_click(coords)
    time.sleep(2)
    solution_check()


if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get('https://blacktoplay.com/?p=608')
    bot.run()

