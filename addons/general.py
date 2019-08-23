import discord
import asyncio
import time
import math
import random
import datetime
import psutil
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

    @commands.command(aliases=['bot', 'info'])
    async def about(self, ctx):
        """ - Display informations about apu bot and latest changes."""
        value = random.randint(0, 0xffffff)

        embed = discord.Embed()
        embed.colour = discord.Colour.blue()
        embed.set_author(name='apu-apustaja.py', icon_url=ctx.author.avatar_url)
        total_members = sum(1 for _ in self.bot.get_all_members())
        total_online = len({m.id for m in self.bot.get_all_members() if m.status is discord.Status.online})
        total_unique = len(self.bot.users)

        #broken, must be fixed
        #now = datetime.datetime.utcnow()
        #delta = now - self.bot.start_time
        #hours, remainder = divmod(int(delta.total_seconds()), 3600)
        #minutes, seconds = divmod(remainder, 60)
        #days, hours = divmod(hours, 24)
        #fmt = '{h}h {m}m {s}s'
        #if days:
        #    fmt = '{d} ' + fmt
        #uptime = fmt.format(h=hours, m=minutes, s=seconds)

        github = '[Click here] (https://github.com/Shinjio/apu-apustaja)'
        server = '[Click here] (https://discord.gg/Mse6VRD)'

        memory_usage = self.bot.process.memory_full_info().uss / 1024**2
        cpu_usage = self.bot.process.cpu_percent() / psutil.cpu_count()

        embed.add_field(name='Author', value='MoonMan#9290', inline=False)
        embed.add_field(name='Guilds', value=len(self.bot.guilds), inline=False)
        embed.add_field(name='Members', value=f'{total_unique} total\n{total_online} online', inline=False)
        embed.add_field(name='Process', value=f'{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU', inline=False)
        embed.add_field(name='Github', value=github, inline=False)
        embed.add_field(name='Discord', value=server, inline=False)
        embed.set_footer(text=f'Powered by discord.py {discord.__version__}')

        await ctx.send(embed=embed)



    #TODO

    #@commands.command(aliases=['calc', 'maths', 'math'])
    #async def calculate(self, ctx, *, formula=None):
    #    """
    #    Do some real fucking math.
    #    """
    #    
    #    author = ctx.message.author
    #    user = ctx.author

    #    if formula == None:
    #        #No fucking math reeeeeeeeeee
    #        msg = f'\u200BUsage: `{ctx.prefix}{ctx.invoked_with} [any maths formula]`'
    #        e = discord.Embed()
    #        e.color = await ctx.get_dominant_color(user.avar_url)
    #        e.description = f'{msg}'
    #        await ctx.send(embed=e)
    #        return
    #    
    #    try:
    #        answer = self.nsp.eval(formula)
    #    except:
    #        #messed up input? examples.
    #        msg = f'\N{THINKING FACE} wrong {formula} input.\nTry any of these:'
    #        e = discord.Embed()
    #        e.color = await ctx.get_dominant_color(user.avatar_url)
    #        e.description = f'\u200B{msg}'

    


def setup(bot):
    bot.add_cog(General(bot))