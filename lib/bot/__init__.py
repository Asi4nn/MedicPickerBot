import re
import discord

from os import listdir
from os.path import sep

from discord import Forbidden
from discord.errors import HTTPException
from discord.ext.commands import Bot as BaseBot, when_mentioned_or, MissingRequiredArgument, MissingPermissions
from discord.ext.commands import CommandNotFound, BadArgument

from lib.helpers.get_current_time import get_current_time

PREFIX = '?'
OWNER_IDS = [164144088818515968]
COGS = []
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

for filename in listdir('./lib/cogs'):
    if filename.endswith('.py'):
        COGS.append(f'lib.cogs.{filename[:-3]}')


def get_prefix(client, message):
    return when_mentioned_or(PREFIX)(client, message)


class Bot(BaseBot):
    def __init__(self):
        self.ready = False
        self.prefix = PREFIX
        self.token = None

        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS, intents=discord.Intents.all())

    def run(self):
        with open(sep.join(["lib", "bot", "TOKEN.txt"]), 'r', encoding="utf-8") as token:
            self.token = token.read()

        self.load_cogs()

        print(get_current_time(), "Bot is running")

        super().run(self.token, reconnect=True)

    def load_cogs(self):
        for cog in COGS:
            self.load_extension(cog)
            print(get_current_time(), f'Loaded cog: {cog}')

    async def on_connect(self):
        print(get_current_time(), "Logged in as {0.user}".format(self))

    async def on_disconnect(self):
        print(get_current_time(), "Bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == 'on_command_error':
            print(get_current_time(), "Something went wrong")
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            # Checks if command looks like currency (matches numbers and periods)
            if not re.match(r'^\$[0-9\.]*$', ctx.message.content.split(' ', 1)[0]):
                await ctx.send(f"Command not found, type {PREFIX}help for a list of commands")

        elif isinstance(exc, BadArgument):
            await ctx.send(f"Bad argument, type {PREFIX}help for a list of commands")
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("Argument(s) are missing from command")
        elif isinstance(exc, HTTPException):
            await ctx.send("Unable to send message (likely too long)")
        elif isinstance(exc, Forbidden):
            await ctx.send("I don't have permission to do that")
        elif isinstance(exc, MissingPermissions):
            await ctx.send("You don't have permission to do that")
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            print(get_current_time(), "Bot is ready")
        else:
            print(get_current_time(), "Bot reconnected")

    # YOU NEED THIS FOR COMMANDS TO WORK
    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
