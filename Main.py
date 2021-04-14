import time
import discord
from discord.ext import commands

startTime = time.time()

client = commands.Bot(command_prefix= "?")

@client.event
async def on_connect():
    print(f'Successfully connected to Discord | Time elapsed: {str(round(time.time() - startTime, 2))} seconds.')

@client.event
async def on_ready():
    print(f'Logged in as {client.user} | Time elapsed: {str(round(time.time() - startTime, 2))} seconds.\nLatency: { str(round(client.latency * 1000))} milliseconds')
#print('Logged in as {0.user}'.format(client))
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