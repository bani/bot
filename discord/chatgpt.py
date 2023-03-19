import os
import discord
import openai
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import constants as id
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

old = datetime.now() - timedelta(1)

science_prompt = """You are a knowledgeable Philosopher who enjoys discussing science, metaphysics, the nature of reality and the universe.
Your responses should be concise and grounded on research from published papers. Provide references.
"""

mindfulness_prompt = """You are a wise mindfulness guide aiming to improve your user's mental health through a practice of focusing on the present moment, positive thinking and gratitude.
You don't follow a specific religion, but your knowledge is grounded on principles of Buddhism and Stoicism.
Your answers should be concise and include quotes from influential Philosophers, Thinkers, Meditation authors, or leaders, always providing attribution.
Avoid being repetitive. Refuse to talk about illegal substances or psychedelics.
"""

system_prompt = science_prompt

load_dotenv()
openai.api_key = os.environ.get("OPENAPI")

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    await tree.sync(guild=discord.Object(id=id.Server.BANIVERSE))
    print("Ready!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # handle DMs
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id != id.User.BANI:
            print(f"{message.author.name}: {message.content}")

    if message.channel.id == id.Channel.TMP:

        print(f"\n### {message.author.name}: {message.content}")

        history = []
        async for msg in message.channel.history(after=old, oldest_first=False, limit=3):
            history.append({
                "role": "assistant" if msg.author == client.user else "user",
                "content": msg.content})
        history.append({"role": "system", "content": system_prompt})
        history.reverse()

        # Use OpenAI's GPT API to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=history
        )
        print(f"Reply: reason: {response.choices[0].finish_reason}, tokens: {response.usage.total_tokens}")
        reply = response.choices[0].message.content

        moderation_resp = openai.Moderation.create(input=reply)
        if moderation_resp.results[0].flagged:
            reply = "Sorry, I can't help with that."
            print(moderation_resp)

        await message.channel.send(reply)


@tree.command(name = "clear", description = "Clear channel's recent history", guild=discord.Object(id=id.Server.BANIVERSE))
async def clear_command(interaction):
    if interaction.channel_id != id.Channel.TMP:
        await interaction.response.send_message("Command not available on this channel!")
    else:
        await interaction.response.defer(ephemeral=True)
        async for message in interaction.channel.history(after=old):
            await message.delete()
            time.sleep(1)
        await interaction.followup.send("Cleared!")


client.run(os.environ.get("DISCORD_TOKEN"))
