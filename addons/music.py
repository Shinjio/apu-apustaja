import discord
import asyncio
import youtube_dl
from discord.ext import commands

class MusicError(commands.UserInputError):
    pass

class Music(commands.Cog):
    """
    Music Cog
    """
    def __init__(self, bot):
        self.bot = bot
        self.music_states = {}
        self.def_volume = 0.1
        self.cur_volume = self.def_volume
        self.queues = {}
        self.players = {}

    @commands.command()
    async def join(self, ctx, *, channel : discord.VoiceChannel = None):
        """
        Joins in a voice channel.
        If no channel is give, joins 
        your current channel.
        """
        if channel is None and not ctx.author.voice:
            raise MusicError('You are not connected in a voice channel nor specified a voice channel for me to join in, fren >:C')
        
        destination = channel or ctx.author.voice.channel

        if ctx.voice_client:
            await ctx.voice_client.move_to(destination)
        else:
            ctx.music_state.voice_client = await destination.connect()

    ##plays music
    #async def play(self, ctx):
    #    """
    #    Joins a voice channel
    #    """
    #    if ctx.voice_client is None or not ctx.voice_client.is_connected():
    #        async ctx.invoke(self.join)


def setup(bot):
    bot.add_cog(Music(bot))