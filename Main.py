from Audio import Audio
import time 
import discord
import sys
import logging
import re
from discord import channel
from discord import message
from discord.ext import commands

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

startTime = time.time()
client = commands.Bot(command_prefix = commands.when_mentioned_or("?"), activity =  discord.Game('bababooey'), description="Vreau sa mor ", intents = discord.Intents.all(), case_insensitive = True)
#command_prefix= "?"
#commands.when_mentioned_or("?")
@client.event
async def on_connect():
     print(f'\nSuccessfully connected to Discord | Time elapsed: {str(round(time.time() - startTime, 2))} seconds.')

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
    if member is None: #if the message has no paramater, the message author becomes one 
        member = ctx.author
    
    await ctx.send(f'{member.avatar_url}')

@Avatar.error
async def info_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        argument = re.findall(r'"(.*?)(?<!\\)"', str(error.args)) #extracts the argument from the error message
        await ctx.send(f'{ argument[0] } is not a member ⚠')

@client.command()
async def Latency(ctx):
    await ctx.send(f'{str(round(client.latency * 1000))}ms')

@client.command()
async def greet(ctx):
    await ctx.send("Say hello!")
    
    def check(message):
            return message.content == 'hello'

    msg = await client.wait_for('message',check=check)
    
    await ctx.send('Hello {.author}!'.format(msg))

@client.command()
async def SendMe(ctx, *, message:str):
    if message:
        await ctx.author.send(message)
    else:
        await ctx.send("Need a parameter ⚠")

@client.command()
async def Message(ctx, member: discord.Member, *, message:str):
        await member.send(message)

@client.command()
async def Upload(ctx, member: discord.Member):
        await member.send(file=discord.File("C:\\Users\\Andrei\\Downloads\\ffworking.mp4"))

client.add_cog(Audio(client))

#cambot: ODMxMzc1OTAwNjE2NDI1NDky.YHUVJA.IKQJdRn5b2I7Spu3Ozei3glkAC4
client.run("ODMxMzc1OTAwNjE2NDI1NDky.YHUVJA.IKQJdRn5b2I7Spu3Ozei3glkAC4")

#sterbot: ODMxMTcxNzA0Mjk3NzUwNTI4.YHRW-A.wVmnrc4F8xfwX5kbjWIPrGmPa6s
#client.run("ODMxMTcxNzA0Mjk3NzUwNTI4.YHRW-A.wVmnrc4F8xfwX5kbjWIPrGmPa6s")