import discord
from discord.ext import commands
import youtube_dl
import pafy
import tokens
import ffmpeg
import asyncio

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready....")
    
class Player(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.song_queue = {}
        self.setup()
        
    def setup(self):
        for guild in self.bot.guilds:
            self.song_queue[guild.id] = []
            
    @commands.command()
    async def join(self,ctx):
        if ctx.author.voice is None:
            return await ctx.send("You are not connected to a voice voice channel,please connect to the channel you want the bot join")
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            
        await ctx.author.voice.channel.connect()
        
    @commands.command()
    async def leave(self,ctx):
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()
        await ctx.send("I am not connected to a voice channel")
        
    async def search_song(self,amount,song,get_url = False):
        info = await self.bot.loop.run_in_executor(None,lambda: 
        youtube_dl.YoutubeDL({"format":"bestaudio","quiet":True})
        .extract_info(f"ytsearch{amount}: {song}",download = False,ie_key="YoutubeSearch"))
        if len(info["entries"]) == 0:
            return None
        else:
            return [entry["webpage_url"] for entry in info["entries"]] if get_url else info
        
    @commands.command()
    async def search(self,ctx,*,song=None):
        if song is None:
            return await ctx.send("you forgot to include a song to search for")
        await ctx.send("searching for song,this may take a few seconds")
        
        info = await self.search_song(5,song)
        embed = discord.Embed(title=f"Result for'{song}':",description = "You can use these URLS to play an exact song \n",colour = discord.Colour.red())
        amount = 0
        for entry in info["entries"]:
            embed.description +=f"[{entry['title']}]({entry['webpage_url']})\n"
            amount+=1
        embed.set_footer(text=f"Displaying the first{amount} results")
        await ctx.send(embed = embed)
        
    async def play_song(self,ctx,song):
        #handle song where song is the url
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)),after = lambda error:self.bot.loop.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5
    
    @commands.command()
    async def play(self,ctx,*,song = None):
        if song == None:
            return await ctx.send("you must include a song to playy")
        if ctx.voice_client is None:
            return await ctx.send("I must be in a voice channel to play a song")
        #handle song where song is not the url
        if not("youtube.com/watch?" in song or "https://youtube/" in song):
            await ctx.send("searching for song,this may take a few seconds")
            result = await self.search_song(1,song,get_url=True)
            
            if result is None:
                return await ctx.send("sorry, i could not find the given song")
            song = result[0]
            
        if ctx.voice_client.source is not None:
            queue_len = len(self.song_queue[ctx.guild.id])
            if queue_len < 10:
                self.song_queue[ctx.guild.id].append(song)
                return await ctx.send(f"I am currently playing a song,this song has been added to the queue at position:{queue_len+1}")
            else:
                return await ctx.send("sorry, i acn only queue up yo 10 songs,please wait for the current to finish")
        await self.play_song(ctx,song)
        await ctx.send(f"now playing:{song}")
        
    async def check_queue(self,ctx):
        if len(self.song_queue[ctx.guild.id])>0:
            await self.play_song(ctx,self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)
               
    @commands.command() 
    async def queue(self,ctx):
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send("there are currently mno songs in the queue")
        embed = discord.Embed(title=f"song queue:",description = " ",colour = discord.Colour.dark_gold())
        i = 1
        for url in self.song_queue[ctx.guild.id]:
            embed.description +=f"{i} ) {url}\n"
            i+=1
        await ctx.send(embed = embed)

    @commands.command()
    async def pause(self,ctx):
        if ctx.voice_client.is_paused():
            return await ctx.send("i am already paused")
        ctx.voice_client.pause()
        await ctx.send("the current song has been paused!")
            
    @commands.command()
    async def resume(self,ctx):
        if ctx.voice_client is None:
            return await ctx.send("i am not connected to voice channel")
        if not ctx.voice_client.is_paused():
            return await ctx.send("i am already playing a song")
        ctx.voice_client.resume()
        await ctx.send("the current song has been resumed!")
        
    @commands.command()
    async def skip(self,ctx):
        if ctx.voice_client is None:
            return await ctx.send("i am not playing any song")
        if ctx.author.voice is None:
            return await ctx.send("you are not connected to voice channel")
    
        
        if ctx.voice_client is not None:
            ctx.voice_client.stop()
        
                
async def setup():
    await bot.wait_until_ready()
    bot.add_cog(Player(bot))
        
bot.loop.create_task(setup())
token = tokens.Token
bot.run(token) 

        
        
        
    