import discord
from discord.ext import commands

client = commands.Bot(command_prefix= "?")

@client.event
async def on_ready():
    print("Online")

client.run("ODMxMzc1OTAwNjE2NDI1NDky.YHUVJA.IKQJdRn5b2I7Spu3Ozei3glkAC4")