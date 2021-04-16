import time 
import discord
from discord.ext import commands

startTime = time.time()
#client = discord.Client(intents=discord.Intents.all())
client = commands.Bot(command_prefix= "?",intents = discord.Intents.all(), case_insensitive = True)

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
    if member.guild.system_channel is not None:
        await member.guild.system_channel.send(f'{member.mention} has joined {member.guild}')

@client.event
async def on_member_remove(member):
    if member.guild.system_channel is not None:
         await member.guild.system_channel.send(f'{member.mention} has left {member.guild}')

@client.command()
async def Avatar(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    await ctx.send(f'{member.avatar_url}')

@client.command()
async def Latency(ctx):
    await ctx.send(f'{str(round(client.latency * 1000))}ms')

client.run("ODMxMzc1OTAwNjE2NDI1NDky.YHUVJA.IKQJdRn5b2I7Spu3Ozei3glkAC4")