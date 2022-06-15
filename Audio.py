from asyncio.tasks import wait
from os import name
from asyncio.queues import Queue
import re
import discord
from discord import player
from discord.ext import commands
import asyncio
import youtube_dl
import typing
from datetime import date
from datetime import datetime
import queue
import time
import sys


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
    async def from_url(cls, url, *, loop=None, stream=False, time_stamp=0):
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': f'-vn -ss {time_stamp}'
            }

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)



class Audio(commands.Cog):
    player_list = None #the links are processed into player objects
    address_list = None
    current_address = None
    current_player = None
    def __init__(self, bot):
        self.bot = bot
        self.player_list = []
        self.address_list = []
        self.current_address = ""
        self.current_player = None
    
    def append_player_list(self, object):
        self.player_list.append(object)

    def remove_player_list(self, index):
        self.player_list.pop(index)

    def get_player_list(self):
        return self.player_list

    def clear_player_list(self):
        self.player_list.clear()

    def insert_player_list(self, index, object):
        self.player_list.insert(index , object)

    def append_address_list(self, object):
        self.address_list.append(object)

    def remove_address_list(self, index):
        self.address_list.pop(index)

    def get_address_list(self):
        return self.address_list

    def clear_address_list(self):
        self.address_list.clear()

    def insert_address_list(self, index, object):
        self.address_list.insert(index , object)

    def get_current_player(self):
        return self.current_player

    def set_current_player(self, object):
        self.current_player = object

    def get_current_address(self):
        return self.current_address

    def set_current_address(self, object):
        self.current_address = object

    async def playlist(self, ctx):
        while(ctx.voice_client is not None):
            while(ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
                    await asyncio.sleep(1)
            else: #if its not playing anything add the new link 
                if len(self.get_player_list()) != 0:
                    #self.current_player = self.player_list[0]
                    self.set_current_player(self.get_player_list()[0])
                    self.set_current_address(self.get_address_list()[0])
                    ctx.voice_client.play(self.get_current_player(), after=lambda e: print(f'Player error: {e}') if e else None)
                    await ctx.send(f'Now playing: {self.get_current_player().title}')
                    self.remove_address_list(0)
                    self.remove_player_list(0)
                    await self.playlist(ctx)
                else:
                    seconds = 10
                    await ctx.send(f'Playlist is empty, will leave in {seconds} seconds if nothing gets submitted')
                    await asyncio.sleep(seconds) #seconds it waits before it leaves
                    if (ctx.voice_client.is_playing() or ctx.voice_client.is_paused() or len(self.get_player_list()) != 0):
                        print("ENDING THREAD")
                        sys.exit()
                    else:
                        await ctx.voice_client.disconnect()
                        await ctx.send(f'Leaving {ctx.author.voice.channel} due to inactivity')
                    
    @commands.command(aliases=['p', 'add'])
    async def play(self, ctx, address, time_stamp:typing.Optional[int] = 0): #this optional thingy should handle a bad parse attempt
            if ctx.author.voice is not None: #if the author is in a voice channel
                if ctx.voice_client is None: #if its not already connected
                    await ctx.author.voice.channel.connect()
                
                async with ctx.typing():
                    self.append_address_list(address)
                    self.append_player_list(await YTDLSource.from_url(address, loop=self.bot.loop, stream=True, time_stamp=time_stamp))
                    #buffers the link
                if(len(self.get_player_list()) == 1 and ctx.voice_client.is_playing()  == False  and ctx.voice_client.is_paused() == False): #prevents the start of a second recursive method
                    print('STARTED A THREAD')
                    await self.playlist(ctx)
                else:
                    #await ctx.send(f'Added {self.player_list[len(self.player_list)-1].title} to playlist.')
                    await ctx.send(f'Added {self.get_player_list()[-1].title} to playlist.')
            else:
                await ctx.send("You must be in a voice channel ⚠")

    @commands.command(aliases=['leave'])
    async def disconnect(self, ctx):
        async with ctx.typing():
            await ctx.voice_client.disconnect()
            self.clear_player_list()
            self.clear_address_list()
            self.set_current_player(None)
            self.set_current_address(None)#cleans up the variables
            await ctx.send(f'Leaving {ctx.author.voice.channel}')
    
    @commands.command(aliases=['remove'])
    async def skip(self, ctx,*index: commands.Greedy[int]): #if the user tries to pass a word instead of a number this greedy thingy should handle it 
        async with ctx.typing():
            if ctx.voice_client is not None:
                if len(index) == 0: #if no special arguments just remove the current url thats playing
                    ctx.voice_client.stop()
                    await ctx.send(f'Skipped: {self.get_current_player().title}')
                else:
                    skip_string = "These have been skipped:"
                    wrong_index = False
                    skip = False
                    for x in range(len(index)):
                        if isinstance(index[x], int):
                        
                            if index[x] <= len(self.get_player_list()) and index[x] >= 0:
                                
                                if index[x] == 0: #skips the current url
                                    ctx.voice_client.stop()
                                    skip_string += f'\n{index[x]}. {self.get_current_player().title}'
                                    skip = True
                                else:
                                    skip_string += f'\n{index[x]}. {self.get_player_list()[index[x]-1].title}'
                                    self.remove_player_list(index[x]-1)
                                    skip = True
                            else:
                                wrong_index = True

                    if skip == False: #if it didnt manage to remove anything clear the "these have been skipped" part of the message
                        skip_string = ""

                    #tried to make it more user friendly, overall its just shit 
                    if wrong_index == True:
                        skip_string = 'Index out of range ⚠\n' + skip_string

                    await ctx.send(skip_string)
            else:
                await ctx.send("Client is not in a channel ⚠")

    @commands.command(aliases=['list', 'playlist'])
    async def queue(self, ctx):
        async with ctx.typing():
            audio_queue = f'Now playing: {self.get_current_player().title}'
            
            for x in range(len(self.get_player_list())):
                audio_queue += f'\n{str(x+1)}. {self.get_player_list()[x].title}'
            
            await ctx.send(audio_queue)

    @commands.command(aliases=['move'])
    async def switch(self, ctx, first_index:typing.Optional[int] = None, second_index:typing.Optional[int] = None):
        async with ctx.typing():
            if len(self.get_player_list()) > 0:
                if first_index == None or second_index == None:
                    await ctx.send("Bad parameter ⚠ \nEnter a number (eg: 5, 1)")
                elif first_index == second_index:
                    await ctx.send("Equal parameters ⚠")
                elif first_index <= len(self.get_player_list()) and second_index <= len(self.get_player_list()) and first_index  >= 0 and second_index >= 0:
                    if first_index == 0 or second_index == 0: #0 represents the currently playing link
                        bigger_index = max(first_index, second_index)
                        ctx.voice_client.stop()
                        ctx.voice_client.play(self.get_player_list()[bigger_index-1], after=lambda e: print(f'Player error: {e}') if e else None)
                        self.remove_player_list(bigger_index-1)
                        await ctx.send(f'Switched playlist positions between {first_index} and {second_index}')
                        #currently it does not switch places between the currently playing and the other index
                        #instead it skips the currently playing and plays the other index
                    else:
                        self.get_player_list()[first_index-1], self.get_player_list()[second_index-1] = self.get_player_list()[second_index-1], self.get_player_list()[first_index-1]
                        await ctx.send(f'Switched playlist positions between {first_index} and {second_index}')
                        #this method is fucked, needs replacing with the player list setter 
                else:
                    await ctx.send("Parameters out of range ⚠")
            else:
                await ctx.send("Playlist is empty ⚠")
    
    @commands.command(aliases=['goTo', 'find'])
    async def seek(self, ctx, time_stamp:typing.Optional[int] = None):
        if(time_stamp == None):
            await ctx.send('Bad timestamp ⚠')
        
        self.insert_address_list(0, self.get_current_address())
        self.insert_player_list(0, await YTDLSource.from_url(self.get_current_address(), loop=self.bot.loop, stream=True, time_stamp=time_stamp))
        ctx.voice_client.stop()

    @commands.command(aliases=['playAgain', 'again']) #replays the last song, has like 50 bugs so its nowhere near functional
    async def replay(self, ctx):
        if ctx.author.voice is not None:
            if ctx.voice_client is not None:
                #self.address_list.insert(0, self.get_current_address())
                #self.player_list.insert(0, await YTDLSource.from_url(self.get_current_address(), FFMPEG_DEFAULT_OPTIONS ,loop=self.bot.loop, stream=True))
                self.insert_address_list(0, self.get_current_address())
                self.insert_player_list(0, await YTDLSource.from_url(self.get_current_address(), loop=self.bot.loop, stream=True) )
                if(ctx.voice_client.is_playing):
                    ctx.voice_client.stop()

    @commands.command(aliases=['keep', 'send']) #dms the author the title
    async def save(self, ctx):
        if ctx.voice_client is not None:
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused() :
                time = datetime.now()

                await ctx.author.send(f'Played: {self.get_current_player().title} on {time.strftime("%d/%m/%Y %H:%M:%S")}\n{self.get_current_address()}')
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