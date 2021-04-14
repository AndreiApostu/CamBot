import time 
import discord
from discord.ext import commands

class BotClient(discord.Client):
    startTime = time.time() #Registers when the code started running

    #client = commands.Bot(command_prefix= "?")
    #client = discord.Intents.all()

    async def on_connect(self):
        print(f'Successfully connected to Discord | Time elapsed: {str(round(time.time() - self.startTime, 2))} seconds.')

    async def on_ready(self):
        print(f'Logged in as {self.user} | Time elapsed: {str(round(time.time() - self.startTime, 2))} seconds.\nLatency: { str(round(self.latency * 1000))} milliseconds')

    async def on_disconnect(self):
        print(f'Lost connection to Discord | Time elapsed: {str(round(time.time() - self.startTime, 2))} seconds.')

    async def on_member_join(self, member):
        print("A")
        if member.guild.system_channel is not None:
            print("B")
            await member.guild.system_channel.send(f'{member.mention} has joined {member.guild}')

    async def on_member_remove(self, member):
        print("A")
        if member.guild.system_channel is not None:
            print("B")
            await member.guild.system_channel.send(f'{member.mention} has left {member.guild}')