import discord
from discord.ext import commands, tasks

#Cog to test commands
class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Test command
    @commands.command()
    async def test(self, ctx):
        print("Test command used")
        await ctx.send("Test String")

async def setup(bot):
    await bot.add_cog(TestCog(bot))