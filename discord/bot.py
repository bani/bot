import os
import discord
import csv
from dotenv import load_dotenv
import re
import time
from datetime import date, datetime
import constants as id

class BotClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.reactions = {
            re.compile('good ?morning', re.IGNORECASE): id.Emoji.SUN,
            re.compile('good ?night', re.IGNORECASE): id.Emoji.MOON,
        }
        self.mention = re.compile('<@!684503427782672517>')
        self.banibot = re.compile('BaniBot', re.IGNORECASE)
        self.time_re = re.compile('(?P<hh>\d{1,2})(?P<mm>:\d{1,2})?[ ]?(?P<md>am|pm)', re.IGNORECASE)

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
                    await self.send(message)
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
            else:
                print('DM from {0.author}: {0.content}'.format(message))
            return
        
        # handle channel messages
        if message.channel.id in (id.Channel.TMP, id.Channel.EVHOME):
            if self.banibot.search(message.content) or (self.mention.search(message.content) and message.content.count('@') == 1):
                await message.add_reaction(self.get_emoji(id.Emoji.BOT))
                return
            for pattern, emoji in self.reactions.items():
                if pattern.search(message.content):
                    await message.add_reaction(self.get_emoji(emoji))

    async def send(self, message):
        try:
            match = re.compile('\$say ([A-Z]+) (.*)').search(message.content)
            channel = self.get_channel(getattr(id.Channel, match[1]))
            await channel.send(match[2])
        except:
            await message.author.send('Format is: $say CHANNEL message')
            return

    async def react(self, message):
        try:
            match = re.compile('\$react ([A-Z]+) ([A-Z]+) ([\d]+)').search(message.content)
            channel = self.get_channel(getattr(id.Channel, match[2]))
            await (await channel.fetch_message(match[3])).add_reaction(client.get_emoji(getattr(id.Emoji, match[1])))
        except:
            await message.author.send('Format is: $react EMOJI CHANNEL message_id')
            return

    async def unreact(self, message):
        try:
            match = re.compile('\$unreact ([A-Z]+) ([A-Z]+) ([\d]+)').search(message.content)
            channel = self.get_channel(getattr(id.Channel, match[2]))
            await (await channel.fetch_message(match[3])).remove_reaction(client.get_emoji(getattr(id.Emoji, match[1])), self.user)
        except:
            await message.author.send('Format is: $unreact EMOJI CHANNEL message_id')
            return

    async def time_conversion(self, message):
        try:
            m = self.time_re.search(message.content)
            time_parts = m.groupdict()
            today = date.today()
            time_str = f"{today.strftime('%Y-%m-%d')} {time_parts['hh']}{time_parts['mm'] if 'mm' in time_parts and time_parts['mm'] else ':00'} {time_parts['md']}"
            datetime_object = datetime.strptime(time_str, '%Y-%m-%d %I:%M %p')
            unix_time = time.mktime(datetime_object.timetuple())
            await message.author.send(f"`<t:{int(unix_time)}:t>`")
        except:
            print("Invalid time")
            return 

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
