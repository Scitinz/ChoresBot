import discord
from discord.ext import commands, tasks

import bin

from datetime import datetime, timedelta

#Cog containing the commands for managing the ChoresBot
class ChoreBotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rota_ctx = None
        self.channel_members = list()
        self.rota_members = list()
        self.lastbincollecttime = None
        self.lastbincollect = None
        self.binsout = False

    #Shutdown command
    @commands.command()
    async def stop(self, ctx):
        print("Shutting down...")
        await self.bot.close()
        exit()

    @commands.command()
    async def hello(self, ctx):
        print("Hello command used")
        await ctx.send("Hello!")

    @commands.command()
    async def beans(self, ctx):
        print("Beans command used")
        await ctx.send("on toast")

    #Get the next collection and send it in the channel that invoked the command
    @commands.command()
    async def nextcollection(self, ctx): 
        print("Next collection command used")
        await ctx.send(bin.getnextcollection())

    #Start a bin rota in the channel that invoked this command
    @commands.command()
    async def beginbinrota(self, ctx, *, arg=""):
        print("Bin rota command used")
        self.rota_ctx = ctx
        #Only auto add members if we haven't specified the no_members argument
        if arg != "no_members":
            self.rota_members = ctx.channel.members
            #Remove the bot from the rota members list
            for member in self.rota_members:
                if self.bot.user.id == member.id:
                    self.rota_members.remove(member)
        #Add all channel members to a different list
        self.channel_members = ctx.channel.members
        self.member_turn_idx = 0
        await ctx.send("Starting bin rota in this channel.")
        #Start the background task
        self.binrota.start()
    
    #Stop the bin rota
    @commands.command()
    async def stopbinrota(self, ctx):
        print("Stop bin rota command used")
        self.binrota.cancel()

    #Add a channel member to the rota
    @commands.command()
    async def addtorota(self, ctx, *args):
        print("Add to rota command used")
        if self.binrota.is_running():
            for member in self.channel_members:
                if member.mentioned_in(ctx.message):
                    if member not in self.rota_members:
                        self.rota_members.append(member)
                        await ctx.send("Added " + member.mention + " to the bin rota.")
                    else:
                        await ctx.send(member.mention + " is already in this bin rota!")
        else:
            await ctx.send("Bin rota is not currently active! Use \"!beginbinrota\" to start.")

    #Remove a channel member from the rota
    @commands.command()
    async def removefromrota(self, ctx):
        print("Remove from rota command used")
        if self.binrota.is_running():
            for member in self.channel_members:
                if member.mentioned_in(ctx.message):
                    if member not in self.rota_members:
                        await ctx.send(member.mention + " is not in this bin rota!")
                    else:
                        await ctx.send("Removed " + member.mention + " from the bin rota.")
                        self.rota_members.remove(member)
        else:
            await ctx.send("Bin rota is not currently active! Use \"!beginbinrota\" to start.")

    #The actual bin rota task
    @tasks.loop(hours=1)
    async def binrota(self):
        #Get next bin info
        binfo = bin.getnextcollectioninfo()
        #Convert this to a date time
        nextbintime = datetime.strptime(binfo['DATE'], '%A %d %B')
        nextbintime = nextbintime.replace(datetime.now().year)

        now = datetime.now()

        #Five hours before this, make an @ (should be at roughly 7 o'clock at night, AKA 19:00)
        if now + timedelta(hours=4) < nextbintime and now + timedelta(hours=5) > nextbintime:
            mention_str = "<@" + str(self.rota_members[self.member_turn_idx].id) + ">"
            await self.rota_ctx.send(mention_str + " please take out the " + binfo['BINS'])
            self.member_turn_idx = (self.member_turn_idx + 1) % len(self.rota_members)
            self.lastbincollecttime = nextbintime
            self.lastbincollect = binfo['BINS']
            self.binsout = True

        if self.binsout:
            #Eleven hours after this, make an @ (should be at roughly 11 o'clock in the morning, AKA 11:00)
            if self.lastbincollecttime + timedelta(hours=11) < now and self.lastbincollecttime + timedelta(hours=12) > now:
                mention_str = "<@" + str(self.rota_members[self.member_turn_idx].id) + ">"
                await self.rota_ctx.send(mention_str + " please bring in the " + self.lastbincollect)
                self.member_turn_idx = (self.member_turn_idx + 1) % len(self.rota_members)
                self.binsout = False

    #Before we start the loop, send a message saying it's been started
    @binrota.before_loop
    async def before_binrota(self):
        await self.rota_ctx.send("Started bin rota in this channel.")

def setup(bot):
    bot.add_cog(ChoreBotCog(bot))