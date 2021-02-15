import os
import discord
import csv
from dotenv import load_dotenv

class BotClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        if message.author == self.user:
            return
        if message.author.id == 227549003296800768: #me
            # user rank
            if message.content.startswith('$user_rank'):
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
            # word cloud
            elif message.content.startswith('$word_cloud'):
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
