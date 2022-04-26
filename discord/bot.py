import os
import discord
import csv
import requests
import re
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from json import loads
from dotenv import load_dotenv
from discord.ext import tasks
import constants as id
import calendar_parser

class BotClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.reactions = {
            re.compile('good ?morning', re.IGNORECASE): id.Emoji.SUN,
            re.compile('good ?night', re.IGNORECASE): id.Emoji.MOON,
        }
        self.mention = re.compile('<@!684503427782672517>')
        self.banibot = re.compile('BaniBot', re.IGNORECASE)
        self.time_re = re.compile('(?P<dt>\d{4}-\d{2}-\d{2})? ?(?P<hh>\d{2})(?P<mm>:\d{2})', re.IGNORECASE)

        self.last_reminder = datetime.now() - timedelta(days=5)
        self.reminder_task.start()

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        # ignore own messages
        if message.author == self.user:
            return

        # handle DMs
        if isinstance(message.channel, discord.DMChannel):
            if message.author.id == id.User.BANI:
                if message.content.startswith('$say'):
                    await self.say(message)
                if message.content.startswith('$emoji'):
                    await self.emoji(message)
                if message.content.startswith('$del'):
                    await self.delete(message)
                if message.content.startswith('$embed'):
                    await self.embed(message)
                if message.content.startswith('$react'):
                    await self.react(message)
                if message.content.startswith('$unreact'):
                    await self.unreact(message)
                elif message.content.startswith('$time'):
                    await self.time_conversion(message)
                elif message.content.startswith('$user_rank'):
                    await self.user_rank(message)
                elif message.content.startswith('$word_cloud'):
                    await self.word_cloud(message)
                elif message.content.startswith('$test'):
                    msg = await self.get_channel(id.Channel.TMP).fetch_message(945151773771960410)
                    print(msg.content)
            else:
                print('DM from {0.author}: {0.content}'.format(message))
            return
        
        # handle channel messages
        if message.channel.id in (id.Channel.TMP, id.Channel.EVHOME):
            # BaniBot mentions
            if self.banibot.search(message.content) or (self.mention.search(message.content) and message.content.count('@') == 1):
                await message.add_reaction(self.get_emoji(id.Emoji.BOT))
                return
            
            # emoji reactions regexp
            for pattern, emoji in self.reactions.items():
                if pattern.search(message.content):
                    await message.add_reaction(self.get_emoji(emoji))
            
            # Events
            if message.content == '?altspace':
                await self.altspace(message)
            if message.content == '?calendar':
                await self.calendar(message)


    @tasks.loop(minutes=20)
    async def reminder_task(self):
        now = datetime.now()
        if now.day != self.last_reminder.day:
            self.last_reminder = now
            channel = self.get_channel(id.Channel.TMP)
            await channel.send(f'Hello <@!{id.User.BANI}>')

    @reminder_task.before_loop
    async def reminder_task_wait(self):
        await self.wait_until_ready() # wait until the bot logs in


    async def say(self, message):
        try:
            match = re.compile('\$say ([A-Z]+) (.*)').search(message.content)
            channel = self.get_channel(getattr(id.Channel, match[1]))
            await channel.send(match[2])
        except Exception as e:
            print(message.content)
            print(e)

    async def emoji(self, message):
        try:
            match = re.compile('\$emoji ([A-Z]+) (.*)').search(message.content)
            channel = self.get_channel(getattr(id.Channel, match[1]))
            await channel.send(f'<a:e:{getattr(id.Emoji, match[2])}>')
        except Exception as e:
            print(message.content)
            print(e)

    async def delete(self, message):
        try:
            match = re.compile('\$del ([A-Z]+) (.*)').search(message.content)
            channel = self.get_channel(getattr(id.Channel, match[1]))
            msg = await channel.fetch_message(int(match[2]))
            await msg.delete()
        except Exception as e:
            print(message.content)
            print(e)

    async def embed(self, message):
        try:
            match = re.compile('\$embed ([A-Z]+) (.*)', re.MULTILINE|re.DOTALL).search(message.content)
            channel = self.get_channel(getattr(id.Channel, match[1]))

            embed_json = loads(match[2])
            embed = discord.Embed().from_dict(embed_json)

            await channel.send(embed=embed)
        except Exception as e:
            print(message.content)
            print(e)

    async def react(self, message):
        try:
            match = re.compile('\$react ([A-Z]+) ([A-Z]+) ([\d]+)').search(message.content)
            channel = self.get_channel(getattr(id.Channel, match[2]))
            await (await channel.fetch_message(match[3])).add_reaction(client.get_emoji(getattr(id.Emoji, match[1])))
        except Exception as e:
            print(message.content)
            print(e)

    async def unreact(self, message):
        try:
            match = re.compile('\$unreact ([A-Z]+) ([A-Z]+) ([\d]+)').search(message.content)
            channel = self.get_channel(getattr(id.Channel, match[2]))
            await (await channel.fetch_message(match[3])).remove_reaction(client.get_emoji(getattr(id.Emoji, match[1])), self.user)
        except Exception as e:
            print(message.content)
            print(e)

    async def time_conversion(self, message):
        try:
            m = self.time_re.search(message.content)
            time_parts = m.groupdict()
            today = date.today()
            iso_time = f"{time_parts['dt'] if time_parts['dt'] else today}T{time_parts['hh']}{time_parts['mm']}-05:00"
            epoch = datetime.fromisoformat(iso_time).timestamp()

            await message.author.send(f"`<t:{int(epoch)}:t>`")
        except Exception as e:
            print(message.content)
            print(e)

    async def altspace(self, message):
        try:
            page = requests.get("https://account.altvr.com/channels/meditation")
            soup = BeautifulSoup(page.content, 'html.parser')
            div = soup.find("div", {"id": "upcoming-events"})

            events = []
            today = datetime.today().date()

            featured = div.find("a", {"class": "banner"})
            time = featured.find("div", {"class": "banner__header-item"})
            if "LIVE!" in time.text:
                events.append( ("LIVE!", featured.find("div", {"class": "banner__footer"}).text))
            else:
                time = featured.find("div", {"class": "banner__header-item time-info-home"})
                if datetime.fromtimestamp(int(time['data-unix-start-time'])).date() == today:
                    events.append( (time['data-unix-start-time'], featured.find("div", {"class": "banner__footer"}).text))

            tiles = div.find_all("a", {"class": "tile"})
            for tile in tiles:
                time = tile.find("div", {"class": "tile__header-item"})
                if datetime.fromtimestamp(int(time['data-unix-start-time'])).date() == today:
                    events.append( (time['data-unix-start-time'], tile.find("div", {"class": "tile__footer"}).text))
                else:
                    break
            
            if len(events) > 0:
                embed=discord.Embed(title="Altspace events today", url="https://account.altvr.com/channels/meditation",
                    color=0x166099)
                embed.set_author(name="EvolVR", url="https://evolvr.org/", icon_url="https://cdn-content-ingress.altvr.com/uploads/channel/profile_image/983488213811200868/ProfileImageEvolVR.jpg")
                for event in events:
                    embed.add_field(name=event[1], value="LIVE!" if event[0] == "LIVE!" else f"<t:{event[0]}:t>", inline=False)

                await message.channel.send(embed=embed)
            else:
                time = featured.find("div", {"class": "banner__header-item time-info-home"})['data-unix-start-time']
                title = featured.find("div", {"class": "banner__footer"}).text
                await message.channel.send(f"No more events scheduled for today. Next event is <t:{time}:F>: {title}")
        except Exception as e:
            print(message.content)
            print(e)

    async def calendar(self, message):
        try:
            events = calendar_parser.get_events()

            if len(events) > 0:
                embed=discord.Embed(title="Events from EvolVR calendar", url="https://calendar.google.com/calendar/embed?src=c_qc3lsjssl0f2mhrljmptf78430%40group.calendar.google.com&ctz=America%2FToronto&mode=WEEK",
                    color=0x166099)
                embed.set_author(name="EvolVR", url="https://evolvr.org/", icon_url="https://cdn-content-ingress.altvr.com/uploads/channel/profile_image/983488213811200868/ProfileImageEvolVR.jpg")
                for event in events:
                    embed.add_field(name=event[1], value=f"<t:{event[0]}:t>", inline=False)

                await message.channel.send(embed=embed)
            else:
                await message.channel.send(f"No more events scheduled for today.")

        except Exception as e:
            print(message.content)
            print(e)

    async def user_rank(self, message):
        try:
            channel_id = int(message.content.split()[1])
        except:
            print("Invalid channel id")
            return
        counter = {}
        channel = self.get_channel(channel_id)
        async for message in channel.history(limit=100):
            author = message.author.name
            if not author in counter:
                counter[author] = 1
            else:
                counter[author] += 1
        for key, val in counter.items():
            print(key+','+str(val))

    async def word_cloud(self, message):
        try:
            channel_id = int(message.content.split()[1])
        except:
            print("Invalid channel id")
            return
        channel = self.get_channel(channel_id)
        with open('messages.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',  quotechar='"', quoting=csv.QUOTE_ALL)

            async for message in channel.history(limit=100):
                writer.writerow([message.author.name, message.content.replace("\n", " ")])


load_dotenv()
token = os.environ.get("DISCORD_TOKEN")
client = BotClient()
client.run(token)
