import discord
from discord.ext import commands, tasks

#Cog to contain basic commands
class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Shutdown command
    @commands.command()
    async def stop(self, ctx):
        #Only shut down when the admin requests it
        if (ctx.author.User.id == self.bot.admin_ID):
            await ctx.send("Shutting down...")
            print("Shutting down...")
            await self.bot.close()
            exit()
        else:
            await ctx.send("Your are not an admin, and so cannot invoke this command!")
            print("Failed stop command use")

    #Hello command
    @commands.command()
    async def hello(self, ctx):
        print("Hello command used")
        await ctx.send("Hello!")

async def setup(bot):
    await bot.add_cog(BaseCog(bot))