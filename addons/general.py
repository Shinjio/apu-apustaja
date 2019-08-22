import discord
import asyncio
import time
import random
from discord.ext import commands


class General(commands.Cog):
    """
    General Commands
    """

    #Construct
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
    
    @commands.command()
    async def purge(self, ctx, number : int):
        try:
            mgs = [] #list to put all the messages in the log
            async for x in ctx.message.channel.history(limit=number):
                mgs.append(x)
            await ctx.message.channel.delete_messages(mgs)
            time.sleep(0.5)
            await ctx.message.channel.send("{} message(s) deleted, fren :3".format(number))
        except Exception as e:
            await ctx.message.channel.send("{}".format(str(e)))
    
    @commands.command()
    async def embedsay(self, ctx, *, text : str):
        """Figa pupazzo messaggi in embed"""
        color = ''.join([random.choice('0123456789ABCDEF') for x in range(5)])
        color = int(color, 16)

        mgs = []
        async for x in ctx.message.channel.history(limit=1):
            mgs.append(x)
        await ctx.message.channel.delete_messages(mgs)

        normaltext = u"\u2063" * random.randint(1, 10) # generating random number for an empty embed
        data = discord.Embed(description=str(text), colour=discord.Colour(value=color))

        try:
            await ctx.message.channel.send(normaltext, embed=data)
        except:
            await ctx.message.channel.send("Exceptionnigga")


def setup(bot):
    bot.add_cog(General(bot))