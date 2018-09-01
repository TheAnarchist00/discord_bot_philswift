import discord
from discord.ext.commands import Bot
from discord.ext import commands
import random
import asyncio
import youtube_dl
import sys, traceback

#suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(title)s.%(ext)s',
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

ffmpeg_options = {
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
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            #take first item from playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel:discord.VoiceChannel):
        """joins a voice Channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' %e) if e else None)

        await ctx.sent('Now playing: {}'.format(query))

    @commands.command()
    async def yt(self, ctx, *, url):
        """plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error:%s' %e) if e else None)

        await ctx.send('now playing: {}'.format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """stream from a url (same as yt, but doesnt predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'), description='Phil Swift')

game = discord.Game("PATCHING, SEALING, BONDING AND REPAIRING WITH FLEXTAPE!")

rockpaperscissor = "rock", "paper", "scissor"

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    await bot.change_presence(activity=game)
    print(f'Successfully logged in and booted...!')

@bot.command()
async def flextape(ctx):
    await ctx.send('PHIL SWIFT HERE WITH FLEX TAPE THE ONLY TAPE THAT CAN PATCH, BOND, SEAL AND REPAIR')

@bot.command()
async def patch(ctx):
    await ctx.send('https://www.flexsealproducts.com/product/flex-tape/')

@bot.command()
async def bond(ctx):
    await ctx.send('https://www.flexsealproducts.com/product/flex-tape/')

@bot.command()
async def seal(ctx):
    await ctx.send('https://www.flexsealproducts.com/product/flex-tape/')

@bot.command()
async def repair(ctx):
    await ctx.send('https://www.flexsealproducts.com/product/flex-tape/')

@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)

@bot.command()
async def swift(ctx):
    await ctx.send('https://i.redd.it/dhizdesrkra11.jpg')

@bot.command()
async def yaya(ctx):
    await ctx.send('nope')

@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send('{0.name} joined in {0.joined_at}'.format(member))

@bot.command()
async def surprise(ctx):
    await ctx.send('Shameer is a fag')

@bot.command()
async def wot(ctx):
    await ctx.send('https://proxy.duckduckgo.com/iu/?u=http%3A%2F%2Fi.ytimg.com%2Fvi%2FUuCxrgbzxoA%2Fmaxresdefault.jpg&f=1')

@bot.command()
async def goodbot(ctx):
    await ctx.send('Thank you')

@bot.command()
async def doit(ctx):
    await ctx.send('https://i.imgur.com/hoBbGBb.png')

@bot.command()
async def greet(ctx):
    await ctx.send(":smiley: :wave: Hello, there!")

@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))

@bot.command()
async def flavortown(ctx):
    await ctx.send("https://proxy.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.7_gKpI3OQy_UTRIc3TIqYAHaFn%26pid%3D15.1&f=1")

@bot.command()
async def cat(ctx):
    await ctx.send("https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif")

@bot.command()
async def oof(ctx):
    await ctx.send("https://www.youtube.com/watch?v=f49ELvryhao")

@bot.command()
async def jojo(ctx):
    await ctx.send("Shameer is a fag :ok_hand: :weary: :tired_face: :poop:")

@bot.command()
async def fahim(ctx):
    await ctx.send("Definition of a fag")

@bot.command()
async def raiyan(ctx):
    await ctx.send("Should go kill himself")

@bot.command()
async def NOGODNO(ctx):
    await ctx.send("https://www.youtube.com/watch?v=umDr0mPuyQc")

@bot.command()
async def unoreverse(ctx):
    await ctx.send("https://2.bp.blogspot.com/-A8C61g2-Ils/UpjhHKza0FI/AAAAAAAAA_g/Jm5Bt1xPJiA/s1600/reverse.jpg")

@bot.command()
async def nope(ctx):
    await ctx.send("https://www.youtube.com/watch?v=gvdf5n-zI14")

@bot.command()
async def gay(ctx):
    await ctx.send("https://www.youtube.com/watch?v=YaG5SAw1n0c")

@bot.command()
async def rps(ctx):
    await ctx.send(random.choice(rockpaperscissor))

@bot.command()
async def info(ctx):
    embed = discord.Embed(title="Phil Swift", description="A bot that can patch, bond, seal and repair anything.", color=0xeee657)
    
    # give info about you here
    embed.add_field(name="Author", value="TheAnarchist_00")
    
    # Shows the number of servers the bot is member of.
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}")

    await ctx.send(embed=embed)

bot.remove_command('help')

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Phil Swift", description="A bot that can patch, bond, seal and repair anything. List of commands are:", color=0xeee657)

    embed.add_field(name="$greet", value="Gives a nice greet message", inline=False)
    embed.add_field(name="$cat", value="Gives a cute cat gif to lighten up the mood.", inline=False)
    embed.add_field(name="$info", value="Gives a little info about the bot", inline=False)
    embed.add_field(name="$help", value="Gives this message", inline=False)
    embed.add_field(name="$surprise", value="The Truth!", inline=False)
    embed.add_field(name="$goodbot", value="Why Thank you kind stranger", inline=False)
    embed.add_field(name="$roll", value="roll a dice NdN style", inline=False)
    embed.add_field(name="$swift", value="THE MAN, THE MYTH, THE LEGEND, PHIL SWIFT!!!", inline=False)
    embed.add_field(name="$doit", value="do it", inline=False)
    embed.add_field(name="$wot", value="wot", inline=False)
    embed.add_field(name="$flavortown", value="FLAVORTOWN!!!", inline=False)
    embed.add_field(name="$oof", value="oof", inline=False)
    embed.add_field(name="$fahim", value="truth", inline=False)
    embed.add_field(name="$jojo", value="For shameer", inline=False)
    embed.add_field(name="$unoreverse", value="ULTIMATE POWER", inline=False)
    embed.add_field(name="$NOGODNO", value="NO GOD NO", inline=False)
    embed.add_field(name="$nope", value="nope", inline=False)
    embed.add_field(name="$gay", value="HUH GAAAAAAYYY!!!", inline=False)
    embed.add_field(name="$yaya", value="kuro requested it", inline=False)
    embed.add_field(name="$raiyan", value="Raiyan", inline=False)
    embed.add_field(name="$choose", value="Settle the score. Write down the two (or more) choices, and see what the man himself chooses.", inline=False)
    embed.add_field(name="$play", value="Play from my local library (not available atm due to restrictions imposed by my host)", inline=False)
    embed.add_field(name="$yt", value="Play from youtube (more trustworthy than stream)(not available atm due to restrictions imposed by my host)", inline=False)
    embed.add_field(name="$stream", value="stream from youtube (WIP)(not available atm due to restrictions imposed by my host)", inline=False)
    embed.add_field(name="$stop", value="stops in vc (not available atm due to restrictions imposed by my host)", inline=False)
    embed.add_field(name="$rps", value="a very basic rock paper scissors", inline=False)

    await ctx.send(embed=embed)
    
bot.add_cog(Music(bot))
bot.run('BOT_TOKEN', bot=True, reconnect=True)
