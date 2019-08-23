import discord
import os
import addons.checks as checks
from datetime import datetime
from random import randint
from discord.ext import commands


class Events(commands.Cog):
    """
    Events
    """

    #Construct
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
    
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id == 329410106523648002:
            await msg.channel.send("Zitto magrebino.")
            return


def setup(bot):
    bot.add_cog(Events(bot))