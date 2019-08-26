import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.command(name='help')
    async def help_command(self, ctx, *cog):
        try:
            if not cog:
                halp=discord.Embed(title='Cog Listing and Uncatergorized Commands',
                                   description=f'Use `{self.bot.config["bot_prefix"]} help *cog*` to find out more about them!\n(BTW, the Cog Name Must Be in Title Case, Just Like this Sentence.)')
                cogs_desc = ''
                for x in self.bot.cogs:
                    cogs_desc += ('{} - {}'.format(x,self.bot.cogs[x].__doc__)+'\n')
                halp.add_field(name='Cogs:\n\n',value=cogs_desc[0:len(cogs_desc)-1],inline=False)
                cmds_desc = ''
                #for y in self.bot.walk_commands():
                #    if not y.cog_name and not y.hidden:
                #        cmds_desc += ('{} - {}'.format(y.name,y.help)+'\n')
                #halp.add_field(name='Uncatergorized Commands',value=cmds_desc[0:len(cmds_desc)-1],inline=False)
                await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send('',embed=halp)
            else:
                if len(cog) > 1:
                    halp = discord.Embed(title='Error!',description='That is way too many cogs!',color=discord.Color.red())
                    await ctx.message.author.send('',embed=halp)
                else:
                    found = False
                    for x in self.bot.cogs:
                        for y in cog:
                            if x == y:
                                halp=discord.Embed(title=cog[0]+' Command Listing',description=self.bot.cogs[cog[0]].__doc__)
                                for c in self.bot.get_cog(y).get_commands():
                                    if not c.hidden:
                                        halp.add_field(name=c.name,value=c.help,inline=False)
                                found = True
                    if not found:
                        halp = discord.Embed(title='Error!',description='How do you even use "'+cog[0]+'"?',color=discord.Color.red())
                    else:
                        await ctx.message.add_reaction(emoji='✉')
                    await ctx.message.author.send('',embed=halp)
        except Exception as e:
            await ctx.send(e)
        #e = discord.Embed(title='Help', color=discord.Colour.dark_orange())
        #e.set_thumbnail(url=self.bot.user.avatar_url)
        #e.set_footer(text=f'Requested by {ctx.message.author.name}', icon_url=ctx.author.avatar_url)

        ##list all cogs
        #cogs = [c for c in self.bot.cogs.keys()]

        #if cog == 'all':
        #    for cog in cogs:
        #        #list of all commands for each cog
        #        cog_commands = self.bot.get_cog(cog).get_commands()
        #        commands_list = ''
        #        #for comm in cog_commands:
        #        #    commands_list += f'**{comm.name}** - *{comm.description}*\n'
        #        
        #        #add the details to the embed
        #        e.add_field(name=cog, value=cog_commands.name, inline=False)
        #else:
        #    #if cog is specified
        #    cogs = [c.lower() for c in cogs]
        #    if cog.lower() in cogs:
        #        commands_list = self.bot.get_cog(cogs[ cogs.index(cog.lower()) ]).get_commands()
        #        help_text=''

        #        #add details for each command
        #        for command in commands_list:
        #            help_text += f'```{command.name}```\n' f'**{command.description}**\n\n'
        #            if len(command.aliases) > 0:
        #                help_text += f'**Aliases :** `{"`, `".join(command.aliases)}`\n\n\n'
        #            else:
        #                help_text += '\n'
        #            help_text += f'Format: `@{self.bot.user.name}#{self.bot.user.discriminator}' f' {command.name} {command.usage if command.usage is not None else ""}`\n\n\n\n'
        #        
        #        e.description = help_text
        #    else:
        #        await ctx.send('Invalid cog specified, fren. Use `help` to list all cogs')
        #        return
        #
        #await ctx.send(embed=e)
        #
        #return


def setup(bot):
    bot.add_cog(Help(bot))