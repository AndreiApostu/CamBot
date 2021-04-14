import time 
import discord
from discord.ext import commands

startTime = time.time() #Registers when the code started running

client = commands.Bot(command_prefix= "?")
#client = discord.Intents.all()

@client.event
async def on_connect():
    print(f'Successfully connected to Discord | Time elapsed: {str(round(time.time() - startTime, 2))} seconds.')

@client.event
async def on_ready():
    print(f'Logged in as {client.user} | Time elapsed: {str(round(time.time() - startTime, 2))} seconds.\nLatency: { str(round(client.latency * 1000))} milliseconds')

@client.event
async def on_disconnect():
    print(f'Lost connection to Discord | Time elapsed: {str(round(time.time() - startTime, 2))} seconds.')

@client.event
async def on_member_join(member):
    print("A")
    if member.guild.system_channel is not None:
        print("B")
        await member.guild.system_channel().send(f'{member.mention()} has joined {member.guild}')

@client.event
async def on_member_remove(member):
    print("A")
    if member.guild.system_channel is not None:
        print("B")
        await member.guild.system_channel().send(f'{member.mention()} has left {member.guild}')

client.Intents = discord.Intents.all()
client.run("ODMxMzc1OTAwNjE2NDI1NDky.YHUVJA.IKQJdRn5b2I7Spu3Ozei3glkAC4")