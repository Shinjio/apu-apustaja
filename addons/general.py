import discord
import asyncio
import aiohttp
import time
import math
import random
import datetime
import psutil
import operator
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional, ZeroOrMore, Forward, nums, alphas, oneOf)
from addons.utils import imageLookup, urban_define, urban_parse_definition
from discord.ext import commands
from sympy import solve
from ext.utilities import parse_equation


class NumericStringParserForPython3(object):
    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])
    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == '-':
            self.exprStack.append('unary -')

    def __init__(self):
        """
        Need it for the math dawg
        
        expop   :: '^'
        multop  :: '*' || '/'
        addop   :: '+' || '-'
        integer :: ['+' || '-'] '0'..'9'+
        """
        point = Literal(".")
        e = CaselessLiteral("E")
        pi = CaselessLiteral("PI")
        fnumber = Combine(Word("+-"+nums, nums) +
                          Optional(point + Optional(Word(nums))) +
                          Optional(e + Word("+-"+nums, nums)))
        ident = Word(alphas, alphas+nums+"_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        expr = Forward()
        atom = ((Optional(oneOf("- +")) + (pi | e | fnumber |ident + lpar + expr + rpar).setParseAction(self.pushFirst)) | Optional(oneOf("- +")) + Group(lpar + expr + rpar)).setParseAction(self.pushUMinus)
        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
        term = factor + ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
        expr << term + ZeroOrMore((addop + term).setParseAction(self.pushFirst))

        self.bnf = expr
        epsilon = 1e-12
        self.opn = {
                "+" : operator.add,
                "-" : operator.sub,
                "*" : operator.mul,
                "/" : operator.truediv,
                "^" : operator.pow }

        self.fn = {
                "sin" : math.sin,
                "cos" : math.cos,
                "tan" : math.tan,
                "abs" : abs,
                "trunc" : lambda a: int(a),
                "round" : round,
                "sgn" : lambda a: abs(a)>epsilon and cmp(a,0) or 0}
        
    
    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluateStack(s)
        if op in "+-*/^":
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif op == "PI":
            return math.pi # 3.1415926535, if i remember right
        elif op == "E":
            return math.e  # 2.718281828, if i remember right
        elif op in self.fn:
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)

    def evalu(self, num_string, parseAll=True):
        self.exprStack = []
        results=self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val


class General(commands.Cog):
    """
    General Commands
    """

    #Construct
    def __init__(self, bot):
        self.bot = bot
        self.nsp = NumericStringParserForPython3()
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
        #server = '[Click here] (https://discord.gg/Mse6VRD)'

        memory_usage = self.bot.process.memory_full_info().uss / 1024**2
        cpu_usage = self.bot.process.cpu_percent() / psutil.cpu_count()

        embed.add_field(name='Author', value='Kurisu#9290', inline=False)
        embed.add_field(name='Guilds', value=len(self.bot.guilds), inline=False)
        embed.add_field(name='Members', value=f'{total_unique} total\n{total_online} online', inline=False)
        embed.add_field(name='Process', value=f'{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU', inline=False)
        embed.add_field(name='Github', value=github, inline=False)
        #embed.add_field(name='Discord', value=server, inline=False)
        embed.set_footer(text=f'Powered by discord.py {discord.__version__}')

        await ctx.send(embed=embed)
    
    @commands.command(aliases=['av'])
    async def avatar(self, ctx, *, member : discord.Member=None):
        """ - Return someone's avatar url"""
        av = member.avatar_url
        em = discord.Embed(description='requested by:\n{0}'.format(ctx.author))
        em.set_image(url=av)

        try:
            await ctx.send(embed=em)
        except Exception as e:
            await ctx.send(str(e))

    #@commands.command()
    #async def reverse(self, ctx):
    #    #try:
    #    image = await imageLookup(ctx.message.attachments[0].url)
    #    print(image)
    #    #await ctx.send(image)
    #    #except Exception as e:
    #    #    await ctx.send(str(e))

    
    #To improve maybe
    @commands.command(aliases=['calc', 'maths', 'math'])
    async def calculate(self, ctx, *, formula=None):
        """
        Do some real fucking math.
        """
        
        author = ctx.message.author
        user = ctx.author

        if formula == None:
            #No fucking math reeeeeeeeeee
            msg = f'\u200BUsage: `{ctx.prefix}{ctx.invoked_with} [any maths formula]`'
            e = discord.Embed()
            e.color = discord.Colour.red()
            e.description = f'{msg}'
            await ctx.send(embed=e)
            return
        
        try:
            answer = self.nsp.evalu(formula)
        except:
            #messed up input? examples.
            msg = f'\N{THINKING FACE} wrong {formula} input.\nTry any of these:'
            e = discord.Embed()
            e.color = discord.Colour.red()
            e.description = f'\u200B{msg}'
            e.add_field(name='multiplication', value="`num` * `num`", inline=False)
            e.add_field(name='division', value="`num` / `num`", inline=False)
            e.add_field(name='addition', value="`num` + `num`", inline=False)
            e.add_field(name='rest', value="`num` - `num`", inline=False)
            e.add_field(name='exponential', value="`num` ^ `num`", inline=False)
            await ctx.send(embed=e, delete_after=60)
            return
        
        #Correct input prints correct answer
        e = discord.Embed()
        e.color = discord.Colour.red()
        e.add_field(name='Input:', value=f'```{formula}```', inline=False)
        e.add_field(name='Result:', value=f'```{round(answer, 2)}```', inline=False)
        await ctx.send(embed=e)

    #To improve
    @commands.command()
    async def algebra(self, ctx, *, equation):
        e = discord.Embed()
        try:
            parsed = parse_equation(equation)
            eq = parsed[0]
            alpha = parsed[1]
            result = solve(eq, alpha)
            e.color = discord.Color.green()
            e.title = 'Equation'
            e.description = f'```py\n{equation} = 0```'
            e.add_field(name='Result', value=f'```py\n{result}```')
            await ctx.send(embed=e)
        except:
            e.color = discord.Color.green()
            e.title = 'Error'
            e.description = "Your expression must be equal to zero, fren"
            await ctx.send(embed=e)

    #To improve
    @commands.command()
    async def urban(self, ctx, search_term : str, n : int = 1):
        """ - Searches up a term in urban dictionary """

        e = discord.Embed()

        try:
            defined = urban_define(search_term)

            if defined:
                defn = defined['definitions'][n -1]
                owo = ('{i}: {defn}'.format(i=n, defn=defn['definition']))

            e.color = discord.Colour.blurple()
            e.title = f"{search_term} means..\n"
            e.description = owo
            await ctx.send(embed=e)

        except:
            e.color = discord.Colour.red()
            e.title = "Error."
            owo = "Term not found, fren :("
            e.description = owo
            await ctx.send(embed=e)
            return
        

def setup(bot):
    bot.add_cog(General(bot))
