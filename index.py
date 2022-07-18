import json
import discord
from discord.ext import commands
from discord.ext import tasks
import cogs

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

    #When we receive ping, send pong
    async def on_message(self, message):
        if message.author.id == self.user.id:
            return #Don't reply to ourselves

        await self.process_commands(message)

    #DM admin with any errors
    async def dm_error(self, error):
        admin_user = await self.fetch_user(self.admin_ID)
        await admin_user.send(repr(error))

intents = discord.Intents.default()
intents.members = True
bot = chores_bot(command_prefix=com_prefix, intents=intents, admin_ID=admin_ID)
bot.load_extension("cogs")
#Run the client
bot.run(token)