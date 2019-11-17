import logging
import subprocess
import discord
import re
from datetime import datetime
import mysql.connector
from discord.ext import commands
from discord.ext.commands.errors import MissingPermissions

logging.basicConfig(level=logging.INFO, format='[%(name)s %(levelname)s] %(message)s')
logger = logging.getLogger('cog.moderation')
'''
db = mysql.connector.connect(host="localhost",user="localuser",database="cogbot_schema",port=7000)
!!!! Warning: No Password Connection, MUST Restrict User.
Manual Setup is required. Therefore, the bot will not be for total publicity.
'''
db = mysql.connector.connect(host="localhost",user="localuser",database="cogbot_schema",port=7000)
cur = db.cursor()
class Moderation(commands.Cog):
    '''Moderation Cog'''
    def __init__(self,bot):
        self.bot = bot

    @commands.command(name='warnings',aliases=['checkuser','warns'])
    async def warnings(self,ctx,userid:str):
        '''Check the warnings for a user. 
        '''
        await ctx.send('Please wait, connecting to the database...',delete_after=5)
        # ping = userid
        async with ctx.channel.typing():
            uid = userid.replace('<','').replace('>','').replace("@","").replace('!','')
            logger.info('Recieved database command `{}`'.format('select * from offences where id="{}"'.format(uid)))
            cur.execute('select * from offences where id="{}"'.format(str(uid)))
            temp = cur.fetchall()
            if len(temp) == 0:
                embed = discord.Embed(title=f'Warnings for user {uid}',description=f'There are no warning(s) for the user {uid}.')
            else:
                embed = discord.Embed(title=f'Warning(s) for user {uid}',description=f'There are {len(temp)} warning(s) for the user {uid}.')
            for i in temp:
                temp1 = str(i[1]).replace('b','')
                temp1 = temp1.replace("'",'')
                dt = str(i[4]).replace('b','').replace("'",'')
                embed.add_field(name=f'Offence {i[2]}:',value=f'**Details**: {temp1}\n**Warned at:**{dt}',inline=True)
        await ctx.send(embed=embed)

    @commands.command(name='warn')
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def warn(self,ctx,*,stuff:str):
        '''Warn a user (see the usage before using.)
        What a massive rulebreaker you have to warn, eh?
        Usage: User Mention/ID|Offence Details|Brief Description|Warn Times
        No spaces between the pipes(|)
        Warn Times = How many times to warn
        If you don't see any messages, check your input or ask @Kenny_#2763
        '''
        await ctx.send('Please wait while the bot retrives data from the database...',delete_after=5)
        async with ctx.channel.typing():
            splited = stuff.split('|')
            print(splited)
            user = splited[0]
            uid = user.replace('<','').replace('>','').replace("@","").replace('!','')
            details = splited[1]
            brief = splited[2]
            times = splited[3]
            dnt = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            logger.info('Warning {} for {} time(s)'.format(uid,times))
            for i in range(0,int(times)):
                print(f'insert into offences (id,details,count,date,brief) values ("{uid}","{details}",{offencecount},"{dnt}","{brief}")')
                cur.execute(f'select * from offences where id="{uid}"')
                result = cur.fetchall()
                offencecount=len(result)+1
                if brief == " ":
                    brief = "No brief given."
                cur.execute(f'insert into offences (id,details,count,date,brief) values ("{uid}","{details}",{offencecount},"{dnt}","{brief}")')
                db.commit()
                cur.execute(f'select * from offences where id="{uid}"')
            currentoffences = len(cur.fetchall())
            embed = discord.Embed(title=f'Warned user {user}',description=f'User {user} warned.',colour=0xFFCC00)
            embed.add_field(name='Reason',value=f'``{details}``')
            embed.add_field(name='Warned by',value=f'{ctx.author.mention}')
            embed.add_field(name='Warned at',value=f'{dnt} UTC+8')
            embed.add_field(name='Current warns',value=currentoffences)
        await ctx.send(embed=embed)

    @warn.error
    async def warnerror(self,error,ctx):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title='Cannot warn a user',colour=0xFF0000,description='You do not have permission to do so.')
            await ctx.send(embed=embed)
    @commands.command(name="clearwarn")
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def clearwarn(self,ctx,user:str):
        '''Removes all warnings from a user
        '''
        uid = user.replace('<','').replace('>','').replace("@","").replace('!','')
        command = f"delete from offences where id = '{uid}'"
        cur.execute(f'select * from offences where id="{uid}"')
        temp = cur.fetchall()
        warns = len(temp)
        async with ctx.channel.typing():
            cur.execute(command)
            db.commit()
        await ctx.send(embed=discord.Embed(title='Removed warnings.',description=f'Removed {warns} warnings from user {uid}.',colour=0x00FF00))
    
    @clearwarn.error
    async def clearwarnerror(self,error,ctx):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title='Cannot clear warns',description='You do not have the permission to do so.',colour=0xFF0000)
            await ctx.send(embed=embed)

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self,ctx,user:str):
        await ctx.send('<@397029587965575170> is working on the bot. Please wait.\nThe moderation cog is being heavily worked on. Please be patient.')

def setup(bot):
    bot.add_cog(Moderation(bot))
