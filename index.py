import json
import discord
from discord.ext import commands
from discord.ext import tasks
import base_cog
import bins_cog

#Load metadata from JSON file
with open("vars.json") as json_file:
    json_vars = json.load(json_file)

#Set the token variable
token = json_vars['DISCORD_BOT_TOKEN']
#Set command prefix
com_prefix = json_vars['COMMAND_PREFIX']
#Get admin user ID
admin_ID = json_vars['ADMIN_ID']

#Establish a discord client class
class chores_bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_ID = admin_ID

    ## Async methods
    #Print when we're logged in
    async def on_ready(self):
        print('Logged in as {0.user}'.format(self))

    #Default message handler
    async def on_message(self, message):
        if message.author.id == self.user.id:
            return #Don't reply to ourselves

        await self.process_commands(message)

intents = discord.Intents.default()
intents.members = True
bot = chores_bot(command_prefix=com_prefix, intents=intents, admin_ID=admin_ID)
bot.load_extension("base_cog")
bot.load_extension("bins_cog")
#Run the client
bot.run(token)