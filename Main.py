import discord
from discord.ext import commands

client = commands.Bot(command_prefix= "?")

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')
    elif message.content.startswith("shutdown"):
        await message.channel.send("Terminating bot...")
        print("Bot terminated")
        exit()

client.run("ODMxMzc1OTAwNjE2NDI1NDky.YHUVJA.IKQJdRn5b2I7Spu3Ozei3glkAC4")