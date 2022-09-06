import discord
from discord.ext import commands, tasks

#Cog to contain basic commands
class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Shutdown command
    @commands.command()
    async def stop(self, ctx):
        print("Shutting down...")
        await self.bot.close()
        exit()

    #Hello command
    @commands.command()
    async def hello(self, ctx):
        print("Hello command used")
        await ctx.send("Hello!")

def setup(bot):
    bot.add_cog(BaseCog(bot))