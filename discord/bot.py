import os
import discord
import csv
from dotenv import load_dotenv
import re
import constants as id

class BotClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.reactions = {
            re.compile('good ?night', re.IGNORECASE): '\N{LAST QUARTER MOON WITH FACE}',
            re.compile('good ?morning', re.IGNORECASE): '\N{SUN WITH FACE}',
        }

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        # print('Message from {0.author}: {0.content}'.format(message))
        if message.author == self.user:
            return
        if message.author.id == id.User.BANI:
            if message.content.startswith('$user_rank'):
                await self.user_rank(message)

            elif message.content.startswith('$word_cloud'):
                await self.word_cloud(message)
        if message.channel.id in (id.EvolVR.HOME, id.Baniverse.TMP):
            for pattern, emoji in self.reactions.items():
                if pattern.search(message.content):
                    await message.add_reaction(emoji)

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
