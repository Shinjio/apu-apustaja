import sqlite3
import urllib
import re
import requests
import json
from http.cookiejar import CookieJar
from urllib.request import urlopen
from discord.ext import commands
from discord.ext.commands import MemberConverter


class Help(commands.DefaultHelpCommand):
    """
    Custom help command
    """
    def __init__(self):
        pass


#These methods are static since they're used in different addons
async def db_check(bot, msg, cursor, table : str):
    """
    This function is a coroutine.
    
    Checks if table exists.
    :param bot: Bot instance
    :param msg: Message
    :param cursor: Database cursor
    :param table: Table name
    :return: Bool
    """

    try:
        cursor.execute('SELECT 1 FROM {}'.format(table))
        return True
    except sqlite3.Error:
        await bot.send_message(msg.channel, "Table {} is not initialized.\n\nHint: Use 'apu db init' to perform"
                                            "database initialization.".format(table))
        cursor.close()
        return False


async def get_members(bot, msg, name : str, ctx):
    """
    This function is coroutine.

    Gets server member/s.
    Returns array of members in "Username#Discriminator" format/ First member of this array (members[0]) should be
    passed to server.get_member_named() method.
    Members array can be used for similar results outputting.

    :param bot:
    :param msg:
    :param name:
    :return:
    """

    members = []

    #Search member by mention
    #first check if it's mention
    if name.startswith("<@"):
        print("Mention has been passed. Looking for the member...")
        converter = MemberConverter()
        name = await converter.convert(name)
        mem = msg.guild.get_member(name)
        print("Member {} found!".format(mem.name))
        members.append(mem.name + "#" + mem.discriminator)
        return members
    else:
        #Search for a member with specific discriminator
        #Since username cannot contain hash we can safely split it
        if '#' in name:
            print("Name with discriminator has been passed.")
            name_parts = name.split("#")
            for mem in msg.guild.members:
                if name_parts[0].lower() in mem.name.lower() and name_parts[1] in mem.discriminator:
                    print("Member {} found!".format(mem.name))
                    members.append(mem.name + "#" + mem.discriminator)
                    # Since there can be only one specific member with this discriminator
                    # we can return member right after we found him
                    return members
                #if we didn't find any members with this discriminator then there's no point to continue
                if not members:
                    print("No members with this discriminator were found...")
                    await bot.send_message(msg.channel, "No members were found and I don't have any clue who that is.")
                    return None

                #search member by username
                for mem in msg.guild.members:
                    #limit number of results
                    if name.lower() in mem.name.lower() and len(members) < 6:
                        members.append(mem.name + "#" + mem.discriminator)
                
                #search member by nickname
                #if we didn't find any members, then there is possibility that it's a nickname
                if not members:
                    print("Members weren't found. Checking if it's a nickname...")
                    for mem in msg.guild.members:
                        #Limit number of results & check if member has a nick and compare with input
                        if mem.nick and mem.lower() in mem.nick.lower() and len(members) < 6:
                            members.append(mem.name + "#" + mem.discriminator)
                        
                #if no members this time, then return None and error message, else return members
                if not members:
                    print("No members were found")
                    await bot.send_message(msg.channel, "No members were found and I don't have any clue who that is.")
                    return None
                else:
                    if len(members) > 4:
                        await bot.say("There are too many results. Please be more specific.\n\nHere is a list with"
                                      "suggestions:\n"
                                      "{}".format("\n".join(members)))
                        return None
                    else:
                        return members

#for reverse function
async def imageLookup(path):
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17')]
    googlepath = 'https://images.google.com/searchbyimage?image_url=' + path
    source = opener.open(googlepath).read()
    findlinks = re.findall(r'<div class ="rg_meta">{"os":".*?","cb":.*?,"ou":"(.*?)","rh":"',source.decode())
    return findlinks

"""URBANDICTIONARY API"""
API_BASE = 'http://api.urbandictionary.com/v0/'

def urban_define(term):
    """Define `term`"""
    try:
        res = requests.get(API_BASE + 'define', params={'term':term}).json()
    except:
        return None

    #if res['list'] == []:
    #    return None

    return {
        'definitions' : [urban_parse_definition(item) for item in res['list']]
    }

def urban_parse_definition(item):
    return {
        'id' : item['defid'],
        'term' : item['word'],
        'definition' : item['definition'],
        'author' : item['author'],
        'up' : item['thumbs_up'],
        'down' : item['thumbs_down'],
        'score' : item['thumbs_up'] - item['thumbs_down'],
        'link' : item['permalink']
    }
"""END OF API"""


#Cog
class Utils(commands.Cog):
    #Construct
    def __init__(self):
        print('Addon "{}" loaded'.format(self.__class__.__name__))

def setup(bot):
    bot.add_cog(Utils())