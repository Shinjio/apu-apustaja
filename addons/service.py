import sqlite3
import json
import os
import sys
from addons import utils
from addons.checks import checks
from discord.ext import commands
from discord import utils as discord

class Service(commands.Cog):
    """
    Service commands (owner only)
    """

    #Construct
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    #send message
    #async def send(self, ctx, msg):
    #    await self.ctx.send(msg)

    #commands
    @commands.command()
    @checks.is_access_allowed(required_level=9000)
    async def load(self, ctx, name : str):
        extension = "addons.{}".format(name)
        try:
            self.bot.load_extension(extension)
            print("{} loaded".format(extension))
            await ctx.message.channel.send("{} loaded".format(extension))
        except Exception as e:
            print('{} failed to load.\n{}: {}'.format(extension, type(e).__name__, e))
            await ctx.message.channel.send('{} failed to load.\n{}: {}'.format(extension, type(e).__name__, e))
    
    @commands.command()
    @checks.is_access_allowed(required_level=9000)
    async def unload(self, ctx, name: str):
        extension = "addons.{}".format(name)
        self.bot.unload_extension(extension)
        print("{} unloaded".format(extension))
        await ctx.message.channel.send("{} unloaded".format(extension))
    
    @commands.command()
    @checks.is_access_allowed(required_level=9000)
    async def reload(self, ctx):
        """Reload addons, db and config (owner only)"""

        #Reload configuration file so we can apply some settings on the fly
        #might be useful
        with open('config.json') as data:
            self.bot.config = json.load(data)
        
        #TESTING: potentially unsafe and might lead to data corruption.
        #commit all changes and close connection before proceed
        self.bot.db.commit()
        self.bot.db.close()
        #Reinitialize connection to database
        self.bot.db = sqlite3.connect('main.db')

        #reload extensions
        for extension in self.bot.config['extensions']:
            try:
                self.bot.unload_extension(extension['name'])
                self.bot.load_extension(extension['name'])
            except Exception as e:
                print('{} failed to load.\n{}: {}'.format(extension['name'], type(e).__name__, e))
                await ctx.message.channel.send('{} failed to load.\n{}: {}'.format(extension['name'], type(e).__name__, e))
        await ctx.message.channel.send("Reload complete!")

    @commands.command()
    @checks.is_access_allowed(required_level=9000)
    async def shutdown(self, ctx):
        """This kills the bot"""
        
        await ctx.message.channel.send("bye fren :(")

        sys.exit(0)

    @commands.group()
    async def roles(self, ctx):
        """Roles management"""
        if ctx.invoked_subcommand is None:
            msg = "Have you ever tried `apu help roles`? I suggest you to do it now, fren"
            await ctx.message.channel.send(msg)
    
    @roles.command(name="list")
    @checks.is_access_allowed(required_level=3)
    async def roles_list(self, ctx):
        """ - Returns roles list for this server (Level 3)"""
        cursor = self.bot.db.cursor()
        
        if not await utils.db_check(self.bot, ctx.message, cursor, "roles"):
            return
        
        msg = "```List of roles:\n"
        cursor.execute("SELECT * FROM roles WHERE serverid=?", (ctx.message.guild.id,))
        data = cursor.fetchall()
        cursor.close()
        if data:
            for row in data:
                msg += "ID: {} | Role name: {} | Level: {}\n".format(row[1], row[2], row[3])
        else:
            msg += "Empty"
        msg += "```"
        await  ctx.message.channel.send(msg)

    @roles.command(name="add")
    @checks.is_access_allowed(required_level=3)
    async def roles_add(self, ctx, name : str, level : int):
        """ - Add role"""
        cursor = self.bot.db.cursor()

        if not await utils.db_check(self.bot, ctx.message, cursor, "roles"):
            return

        role = discord.get(ctx.message.guild.roles, name=name)

        if role is None:
            print("Role wasn't found")
            await ctx.message.channel.send("Role wasn't found, fren")
            return

        db = self.bot.db

        record = (role.id, role.name.lower(), level, ctx.message.guild.id)
        query = 'INSERT INTO roles(role_id, role, level, serverid) VALUES (?,?,?,?)'

        try:
            db.execute(query, record)
            db.commit()
            #Add role
            self.bot.access_roles[ctx.message.guild.id].update({role.id : level})
            await ctx.message.channel.send("Your record has been successfully added, fren")
        except sqlite3.Error as e:
            await ctx.message.channel.send("Failed to add new record, fren :(\n"
                                           "```{}```".format(str(e)))
    
    @roles.command(name="rm")
    @checks.is_access_allowed(required_level=3)
    async def roles_remove(self, ctx, name : str):
        """ - Remove role"""
        cursor = self.bot.db.cursor()

        if not await utils.db_check(self.bot, ctx, cursor, "roles"):
            return

        role = discord.get(ctx.message.guild.roles, name=name)

        if role is None:
            print("Role wasn't found")
            await ctx.message.channel.send("Role wasn't found, fren")
            return
        
        db = self.bot.db

        record = (role.name.lower(), ctx.message.guild.id)
        query = 'DELETE FROM roles WHERE role=? AND serverid=?'
        if db.execute(query, record).rowcount == 0:
            await ctx.message.channel.send("Failed to remove this record, fren")
        else:
            db.commit()
            #Remove role from storage
            self.bot.access_roles[ctx.message.guild.id].pop(role.id)
            await ctx.message.channel.send("This record has been successfully removed, fren")

    @commands.group()
    async def db(self, ctx):
        """Database management (owner only)"""
        if ctx.invoked_subcommand is None:
            msg = "Have you ever tried `apu help db`? I suggest you to do it now, fren"
            await ctx.message.channel.send(msg)
    
    @db.command(name="init")
    @checks.is_access_allowed(required_level=9000)
    async def db_init(self, ctx):
        """Initializes db (required on first start)"""
        db = self.bot.db

        try:
            roles = [
                ('commander', 3, 87159376091033600), ('moderator', 2, 87159376091033600)
            ]
            db.executemany('INSERT INTO roles(role, level, serverid) VALUES (?,?,?)', roles)
            
            db.commit()

            #put roles in storage
            #role[0] - role name
            #role[1] - access level
            for role in roles:
                self.bot.access_roles[ctx.message.guild.id].update({role[0] : role[1]})
            
            await ctx.message.channel.send("Database has been initialized, fren!")
        except sqlite3.Error as e:
            await ctx.message.channel.send("Failed to initialize db, fren :(")
    
    @db.command(name="add")
    @checks.is_access_allowed(required_level=3)
    async def db_add(self, ctx, table : str, name : str, content : str):
        """ - Add record"""
        db = self.bot.db
        record = ('{}'.format(name), '{}'.format(content))
        query = 'INSERT INTO {} VALUES (?,?)'.format(table)

        try:
            db.execute(query, record)
            db.commit()
            await ctx.message.channel.send("Your record has been successfully added, fren")
        except sqlite3.Error:
            await ctx.message.channel.send("Failed to add new record, fren :(")
        
    @db.command(name="edit")
    @checks.is_access_allowed(required_level=3)
    async def db_edit(self, ctx, table : str, name : str, column : str, value : str):
        """ - Edit record"""
        db = self.bot.db
        record = (name,)
        query = 'UPDATE {} SET {} = "{}" WHERE name=?'.format(table, column, value)
        if db.execute(query, record).rowcount == 0:
            await ctx.message.channel.send("This record wasn't found, fren")
        else:
            db.commit()
            await ctx.message.channel.send("This record has been successfully edited, fren")

    @db.command(name="rm")
    @checks.is_access_allowed(required_level=3)
    async def db_remove(self, ctx, table : str, name : str):
        """ - Remove record"""

        db = self.bot.db
        record = (name,)
        query = 'DELETE FROM {} WHERE name=?'.format(table)
        if db.execute(query, record).rowcount == 0:
            await ctx.message.channel.send("Failed to remove this record, fren")
        else:
            db.commit()
            await ctx.message.channel.send("This record has been successfully removed, fren")

def setup(bot):
    bot.add_cog(Service(bot))