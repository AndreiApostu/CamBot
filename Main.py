import time 
import discord
import sys
import logging
import re

from discord.ext import commands

#logging.basicConfig(level=logging.INFO)

startTime = time.time()
#client = discord.Client(intents=discord.Intents.all())
client = commands.Bot(command_prefix= "?",intents = discord.Intents.all(), case_insensitive = True)

@client.event
async def on_connect():
     print(f'Successfully connected to Discord | Time elapsed: {str(round(time.time() - startTime, 2))} seconds.')

@client.event
async def on_ready():
    print(f'Logged in as {client.user} | Time elapsed: {str(round(time.time() - startTime, 2))} seconds.\nLatency: { str(round(client.latency * 1000))} milliseconds')
    await client.change_presence(activity=discord.Game('Everything i put effort into turns to shit'))

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

@Avatar.error
async def info_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        argument = re.findall(r'"(.*?)(?<!\\)"', str(error.args))
        await ctx.send(f'{ argument[0] } is not a member ⚠')

@client.command()
async def Latency(ctx):
    await ctx.send(f'{str(round(client.latency * 1000))}ms')

@client.command()
async def Shut(ctx):
    await ctx.send('Shutting Down...')
    sys.exit()

client.run("ODMxMzc1OTAwNjE2NDI1NDky.YHUVJA.IKQJdRn5b2I7Spu3Ozei3glkAC4")