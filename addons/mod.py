import discord
import asyncio
import time
from addons import utils
from addons.checks import checks
from discord.ext import commands

class Mod(commands.Cog):
    """
    Moderation commands (owner/mod only)
    """
    
    #construct
    def __init__(self, bot):
        self.bot = bot
        self.timers_storage = bot.unmute_timers
        
        #open cursor and check for mutes in database
        cursor = self.bot.db.cursor()
        #check for members who need to be unmuted now
        self.members_to_unmute(cursor)
        #check for members who need to be unmuted later
        self.members_to_update_mute(cursor)
        #close cursor
        cursor.close()

        print('Addon "{}" loaded'.format(self.__class__.__name__))

    def members_to_unmute(self, cursor):
        cursor.execute("SELECT * FROM mutes WHERE mute_time < strftime('%s','now')")
        to_unmute_now_data = cursor.fetchall()
        if to_unmute_now_data:
            unmute_tasks = []
            print("Users with expired mute found. Removing mutes...")
            for row in to_unmute_now_data:
                # row[0] - ID
                # row[1] - Member ID
                # row[2] - Member name
                # row[3] - Mute time
                # row[4] - server id
                for server in self.bot.guilds:
                    if server.id == row[4]:
                        member = server.get_member(row[1])
                        #since we can't use async in __init__ we'll create Future task
                        task = asyncio.ensure_future(self.set_permission(server, member, None))
                        #add task to array
                        unmute_tasks.appen(task)
                        #add callback so task get removed from array when it's done
                        task.add_done_callback(unmute_tasks.remove)
                        break
            #remove members with expired mute from database
            self.bot.db.execute("DELETE FROM mutes WHERE mute_time < strftime('%s','now')")
            self.bot.db.commit()

    def members_to_update_mute(self, cursor):
        cursor.execute("SELECT * FROM mutes")
        to_unmute_later_data = cursor.fetchall()
        if to_unmute_later_data:
            print("Users with not expired mute found.")
            for row in to_unmute_later_data:
                # row[0] - ID
                # row[1] - Member ID
                # row[2] - Member name
                # row[3] - Mute time
                # row[4] - server id
                for server in self.bot.guilds:
                    if server.id == row[4]:
                        member = server.get_member(row[1])
                        seconds_to_unmute = row[3] - time.time()
                        #prevent creating multiple tasks on 'reload' command
                        if member.id not in self.timers_storage[server.id]:
                            print("Setting up timers...")
                            unmute_timer = self.bot.loop.create_task(self.unmute_timer(server, member, seconds_to_unmute))
                            self.timers_storage[server.id].update({member.id: unmute_timer})
    
    async def set_permission(self, server, member, access):
        #craete empty PermissionOverwrite object and update values
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = access
        overwrite.read_messages = True

        try:
            await member.edit(mute=False if access is None else True)
        except discord.Forbidden as e:
            print("Failed to set user's voice state. Reason: {}".format(type(e).__name__))
        except Exception as e:
            if type(e).__name__ == "HTTPException":
                pass
            else:
                print("{}".format(type(e).__name__))
        
        print("Setting permission for {} to: {}".format(member.name, str(access)))

        for channel in server.channels:
            if channel.type is discord.ChannelType.text:
                #set perms for each channel
                try:
                    await channel.set_permissions(member, overwrite=overwrite)
                except discord.Forbidden as e:
                    print("Failed to change permission in {} channel. Reason: {}".format(channel, type(e).__name__))
    
    async def unmute_timer(self, server, member, seconds : int):
        try:
            await asyncio.sleep(seconds)

            #Reset permission
            await self.set_permission(server, member, None)
            #remove muted member from storage
            self.remove_muted_member(member, server)

            print("Member {} has been unmuted.".format(member.name))

        except asyncio.CancelledError:
            pass

    def remove_muted_member(self, member, guild):
        db = self.bot.db
        values = (member.id, guild.id)
        db.execute("DELETE FROM mutes WHERE member_id=? AND server_id=?", values)
        db.commit()

        del self.timers_storage[guild.id][member.id]
    
    #Commands
    @commands.command()
    @checks.is_access_allowed(required_level=2)
    async def mute(self, ctx, user : discord.Member=None, period=''):
        """ - Mute for specific time."""
        amount = 0
        if period:
            amount = int(period[:-1])
            if amount < 0:
                await ctx.message.channel.send("Invalid amount of time, fren")
                return
        
        server = ctx.message.guild

        #Check for permissions before proceeding
        if not commands.bot_has_permissions(manage_roles=True):
            await ctx.message.channel.send("I'm not able to manage permissions without `Manage Roles` permission")
            return
        elif not commands.bot_has_permissions(mute_members=True):
            await ctx.message.channel.send("I'm not able to mute voice without `Mute Members` permission.")

        if not user:
            await ctx.message.channel.send("Specify a user, fren")
        
        #member = ctx.message.guild.get_member_named(user)

        if user.id in self.timers_storage[server.id]:
            await ctx.message.channel.send("This member is already muted, fren")
            return

        #set permissions
        await self.set_permission(server, user, False)

        if amount:
            multiplier = period[-1] if period[-1] in ('s', 'm', 'h', 'd', 'y') else 's'

            def multiply_time(m, secs):
                return {
                    m == 's': secs * 1,
                    m == 'm': secs * 60,
                    m == 'h': secs * 60 * 60,
                    m == 'd': secs * 60 * 60 * 24,
                    m == 'y': secs * 60 * 60 * 24 * 365,
                }[True]

            period = multiply_time(multiplier, amount)
            period *= 10
            
            #Set unmute timer
            unmute_timer = self.bot.loop.create_task(self.unmute_timer(server, user, period))
            self.timers_storage[server.id].update({user.id: unmute_timer})

            #write muted user to database
            db = self.bot.db
            values = (user.id, user.name, period, server.id)
            db.execute("INSERT INTO mutes(member_id, member_name, mute_time, server_id) VALUES (?,?,strftime('%s','now') + ?,?)", values)
            db.commit()

            def convert_time(secs):
                return {
                    1 <= secs < 60: '{} second(s)'.format(secs),
                    60 <= secs < 3600: '{0[0]} minute(s) {0[1]} second(s)'.format(divmod(secs, 60)),
                    3600 <= secs < 86400: '{0[0]} hour(s) {0[1]} minute(s)'.format(divmod(secs, 60 * 60)),
                    86400 <= secs: '{0[0]} day(s) {0[1]} hour(s)'.format(divmod(secs, 60 * 60 * 24)),
                }[True]
            mute_time = convert_time(period)
            
            await ctx.message.channel.send("Member {} has been muted for {}".format(user.name, mute_time))
        else:
            await ctx.message.channel.send("Member {} has been muted permanently".format(user.name))

    @commands.command()
    @checks.is_access_allowed(required_level=2)
    async def unmute(self, ctx, user : discord.Member=None):
        """- Unmute command"""
        server = ctx.message.guild

        #check for permissions before proceeding
        if not commands.bot_has_permissions(manage_roles=True):
            await ctx.message.channel.send("I'm not able to manage permissions without `Manage Roles` permission.")
        elif not commands.bot_has_permissions(mute_members=True):
            await ctx.message.channel.send("I'm not able to mute voice without `Mute Members` permission.")

        if not user:
            await ctx.message.channel.send("Specify a user, fren")
        
        #reset permissions
        await self.set_permission(server, user, None)

        #remove mute task for a member and remove him from database
        if user.id in self.timers_storage[server.id]:
            self.timers_storage[server.id][user.id].cancel()
            self.remove_muted_member(user, server)
        
        await ctx.message.channel.send("Member {} has been unmuted by command.".format(user.name))

    @commands.command()
    @checks.is_access_allowed(required_level=2)
    async def kick(self, ctx, user : discord.Member=None, *, reason=""):
        """ - Kicks a user"""
        if user:
            try:
                await user.kick(reason=reason)
                return_msg = "Kicked user `{}`".format(user.mention)
                if reason:
                    return_msg += "for reason: `{}`".format(reason)
                return_msg += "."
                await ctx.message.channel.send(return_msg)
            except discord.Forbidden:
                await ctx.message.channel.send("Could not kick user. Not enough permissions fren :(")
        else:
            return await ctx.message.channel.send("Could not find user, fren")
    
    @commands.command(aliases=['hban'])
    @checks.is_access_allowed(required_level=2)
    async def hackban(self, ctx, user_id : int):
        """ - Bans a user outside the server"""
        author = ctx.message.author
        guild = author.guild

        user = guild.get_member(user_id)

        if user is not None:
            return await ctx.invoke(self.ban, user=user)
        
        try:
            await self.bot.http.ban(user_id, guild.id, 0)
            await ctx.message.channel.send("Banned user: {}".format(user_id))
        except discord.NotFound:
            await ctx.message.channel.send("Could not find user.\nInvalid user ID was provided")
        except discord.errors.Forbidden:
            await ctx.message.channel.send("Could not ban user. Not enough permissions fren :(")
    
    @commands.command()
    @checks.is_access_allowed(required_level=2)
    async def ban(self, ctx, user : discord.Member=None, *, reason=""):
        """ - Bans a user"""
        if user:
            try:
                await user.ban(reason = reason)
                return_msg = "Banned user `{}`".format(user.mention)
                if reason:
                    return_msg += "for reason: `{}`".format(reason)
                return_msg += "."
                await ctx.message.channel.send(return_msg)
            except discord.Forbidden:
                await ctx.message.channel.send("Could not ban user. Not enough permissions fren :(")
        else:
            return await ctx.message.channel.send("Could not find user, fren :(")



def setup(bot):
    bot.add_cog(Mod(bot))