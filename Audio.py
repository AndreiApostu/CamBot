from asyncio.tasks import wait
from os import name
from asyncio.queues import Queue
import discord
from discord import player
from discord.ext import commands
import asyncio
import youtube_dl
import typing
from datetime import date
from datetime import datetime

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
    }



ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        

    @classmethod
    async def from_url(cls, url, options, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **options), data=data)



class Audio(commands.Cog):
    playerList = [] #the links are processed into player objects
    addressList = []
    currentTitle = ""
    currentAddress = ""
    currentPlayer = None
    def __init__(self, bot):
        self.bot = bot
        self.currentTitle = ""
        self.playerList = []
        self.addressList = []
        self.currentAddress = ""
        self.currentPlayer = None
        

    async def playlist(self, ctx):
        while(ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
                await asyncio.sleep(1)
        else: #if its not playing anything add the new link 
            if len(self.playerList):
                ctx.voice_client.play(self.playerList[0], after=lambda e: print(f'Player error: {e}') if e else None)
                await ctx.send(f'Now playing: {self.playerList[0].title}')
                self.currentTitle = self.playerList[0].title
                self.currentAddress = self.addressList[0]
                self.currentPlayer = self.playerList[0]
                self.playerList.pop(0)
                self.addressList.pop(0)
                await self.playlist(ctx)
            else:
                seconds = 5
                await ctx.send(f'Playlist is empty, will leave in {seconds} seconds if nothing gets submitted')
                await asyncio.sleep(seconds) #seconds it waits before it leaves
                while(ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
                    break
                else:
                    await ctx.send(f'Leaving {ctx.author.voice.channel} due to inactivity')
                    await ctx.voice_client.disconnect()

    @commands.command(aliases=['p'])
    async def play(self, ctx, address):
            if ctx.author.voice is not None: #if the author is in a voice channel
                if ctx.voice_client is None: #if its not already connected
                    await ctx.author.voice.channel.connect()
                
                async with ctx.typing():
                    self.addressList.append(address)
                    self.playerList.append(await YTDLSource.from_url(address, FFMPEG_OPTIONS ,loop=self.bot.loop, stream=True)) #buffers the link
                if(len(self.playerList) == 1 and ctx.voice_client.is_playing()  == False  and ctx.voice_client.is_paused() == False): #prevents the start of a second recursive method
                    await self.playlist(ctx)
                else:
                    await ctx.send(f'Added {self.playerList[len(self.playerList)-1].title} to playlist.')
            else:
                await ctx.send("You must be in a voice channel ⚠")

    @commands.command(aliases=['leave'])
    async def disconnect(self, ctx):
        async with ctx.typing():
            await ctx.voice_client.disconnect()
            self.playerList.clear
            self.currentTitle = "" #cleans up the list 
            await ctx.send(f'Leaving {ctx.author.voice.channel}')
    
    @commands.command(aliases=['remove'])
    async def skip(self, ctx,*index: commands.Greedy[int]): #if the user tries to pass a word instead of a number this greedy thingy should handle it 
        async with ctx.typing():
            if ctx.voice_client is not None:
                if len(index) == 0: #if no special arguments just remove the current url thats playing
                    await ctx.send(f'Skipped: {self.currentTitle}')
                    ctx.voice_client.stop()
                else:
                    skipString = "These have been skipped:"
                    print(index)
                    wrongIndex = False
                    skip = False
                    for x in range(len(index)):
                        if isinstance(index[x], int):
                        
                            if index[x] <= len(self.playerList) and index[x] >= 0:
                                
                                if index[x] == 0: #skips the current url
                                    ctx.voice_client.stop()
                                    skipString += f'\n{index[x]}. {self.currentTitle}'
                                    skip = True
                                else:
                                    skipString += f'\n{index[x]}. {self.playerList[index[x]-1].title}'
                                    self.playerList.pop((index[x]-1))
                                    skip = True
                            else:
                                wrongIndex = True

                    if skip == False: #if it didnt manage to remove anything clear the "these have been skipped" part of the message
                        skipString = ""

                    #tried to make it more user friendly, overall its just shit 
                    if wrongIndex == True:
                        skipString = 'Index out of range ⚠\n' + skipString

                    await ctx.send(skipString)
            else:
                await ctx.send("Client is not in a channel ⚠")

    @commands.command(aliases=['list', 'playlist'])
    async def queue(self, ctx):
        async with ctx.typing():
            audioQueue = f'Now playing: {self.currentTitle}'
            
            for x in range(len(self.playerList)):
                audioQueue += f'\n{str(x+1)}. {self.playerList[x].title}'
            
            await ctx.send(audioQueue)

    @commands.command(aliases=['move'])
    async def switch(self, ctx, firstIndex:typing.Optional[int] = None, secondIndex:typing.Optional[int] = None):
        async with ctx.typing():
            if len(self.playerList) > 0:
                if firstIndex == None or secondIndex == None:
                    await ctx.send("Bad parameter ⚠ \nEnter a number (eg: 5, 1)")
                elif firstIndex == secondIndex:
                    await ctx.send("Equal parameters ⚠")
                elif firstIndex <= len(self.playerList) and secondIndex <= len(self.playerList) and firstIndex  >= 0 and secondIndex >= 0:
                    if firstIndex == 0 or secondIndex == 0: #0 represents the currently playing link
                        biggerIndex = max(firstIndex, secondIndex)
                        ctx.voice_client.stop()
                        ctx.voice_client.play(self.playerList[biggerIndex-1], after=lambda e: print(f'Player error: {e}') if e else None)
                        self.playerList.pop(biggerIndex-1)
                        await ctx.send(f'Switched playlist positions between {firstIndex} and {secondIndex}')
                        #currently it does not switch places between the currently playing and the other index
                        #instead it skips the currently playing and plays the other index
                    else:
                        self.playerList[firstIndex-1], self.playerList[secondIndex-1] = self.playerList[secondIndex-1], self.playerList[firstIndex-1]
                        await ctx.send(f'Switched playlist positions between {firstIndex} and {secondIndex}')
                else:
                    await ctx.send("Parameters out of range ⚠")
            else:
                await ctx.send("Playlist is empty ⚠")
    
    @commands.command(aliases=['goTo', 'find'])
    async def seek(self, ctx, timeStamp):
        pass

    @commands.command(aliases=['playAgain', 'again'])
    async def replay(self, ctx):
        if ctx.author.voice is not None:
            if ctx.voice_client is not None:
                self.addressList.insert(0, self.currentAddress)
                self.playerList.insert(0, await YTDLSource.from_url(self.currentAddress, FFMPEG_OPTIONS ,loop=self.bot.loop, stream=True))
                if(ctx.voice_client.is_playing):
                    ctx.voice_client.stop()

    @commands.command(aliases=['keep', 'send']) #dms the author the title
    async def save(self, ctx):
        if ctx.voice_client is not None:
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused() :
                time = datetime.now()

                await ctx.author.send(f'Played: {self.currentTitle} on {time.strftime("%d/%m/%Y %H:%M:%S")}\n{self.currentAddress}')
            else:
                await ctx.send("Client is not playing ⚠")
        else:
            await ctx.send("Client is not connected ⚠")

    @commands.command(aliases=['stop'])
    async def pause(self, ctx):
        async with ctx.typing():
            if ctx.voice_client is not None:
                if ctx.voice_client.is_playing():
                    ctx.voice_client.pause()
                    await ctx.send("Client paused")
                else:
                    await ctx.send("Client is not playing ⚠")
            else:
                await ctx.send("Client is not connected ⚠")

    @commands.command(aliases=['resume'])
    async def start(self, ctx):
        async with ctx.typing():
            if ctx.voice_client is not None:
                if  ctx.voice_client.is_paused():
                    ctx.voice_client.resume()
                    await ctx.send("Client resumed")
                else:
                    await ctx.send("Client is already playing ⚠")
            else:
                await ctx.send("Client is not connected ⚠")