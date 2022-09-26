import json
import discord
from discord.ext import commands
from discord.ext import tasks

from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
from threading import Thread
import asyncio
import os

#Load metadata from JSON file
with open("vars.json") as json_file:
    json_vars = json.load(json_file)

#Set the token variable
token = json_vars['DISCORD_BOT_TOKEN']
#Set command prefix
com_prefix = json_vars['COMMAND_PREFIX']
#Set admin user ID
admin_ID = json_vars['ADMIN_ID']

#Class to enable live updates
class ModuleUpdater(RegexMatchingEventHandler):
    def __init__(self, bot):
        super().__init__(regexes=".+\.py", ignore_directories=True, case_sensitive=True)
        self.bot = bot

    #Reload a cog that has been modified
    def on_modified(self, event):
        file_path = event.src_path
        filename = os.path.basename(file_path)
        modulename = filename.split(".")[0]
        #Only reload cogs
        if "cog" in modulename:
            print("Reloading " + modulename)
            asyncio.run(self.bot.reload_extension(modulename))

    #Load a new cog that has been created
    def on_created(self, event):
        file_path = event.src_path
        filename = os.path.basename(file_path)
        modulename = filename.split(".")[0]
        #Only load cogs
        if "cog" in modulename:
            print("Loading " + modulename)
            asyncio.run(self.bot.load_extension(modulename))

#Method for the daemon thread to run to handle code updates
def ModuleUpdateHandler(bot):
    event_handler = ModuleUpdater(bot)
    observer = Observer()
    observer.schedule(event_handler=event_handler, path=".", recursive=False)
    observer.start()
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()

#Establish a discord client class
class ChoresBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_ID = admin_ID

    ## Async methods
    #Print when we're logged in, and load extensions
    async def on_ready(self):
        print('Logged in as {0.user}'.format(self))
        files = os.listdir()
        #Load any file that is a cog
        for file in files:
            if "cog.py" in file:
                name = file.split(".")[0]
                await self.load_extension(name)
        print("Loaded Extensions")

    #Default message handler
    async def on_message(self, message):
        if message.author.id == self.user.id:
            return #Don't reply to ourselves

        await self.process_commands(message)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = ChoresBot(command_prefix=com_prefix, intents=intents, admin_ID=admin_ID)

#Run the daemon thread
updater = Thread(target=ModuleUpdateHandler, daemon=True, args=(bot,))
updater.start()

#Run the client
bot.run(token)