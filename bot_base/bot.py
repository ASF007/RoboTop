import datetime
import sys
import traceback

import discord
import humanize
from discord.ext import commands

from bot_base.blacklist import BlacklistManager
from bot_base.db import MongoManager
from bot_base.exceptions import PrefixNotFound


class BotBase(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.db = MongoManager(kwargs.pop("mongo_url"))
        self.blacklist = BlacklistManager(self.db)
        self.uptime = datetime.datetime.now(tz=datetime.timezone.utc)

        self.DEFAULT_PREFIX = kwargs.pop("default_prefix")

        super().__init__(*args, **kwargs)

    def get_bot_uptime(self):
        return humanize.precisedelta(self.uptime)

    async def get_command_prefix(self, message):
        try:
            prefix = await self.get_guild_prefix(guild_id=message.guild.id)

            if message.content.casefold().startswith(prefix.casefold()):
                # The prefix matches, now return the one the user used
                # such that dpy will dispatch the given command
                prefix_length = len(prefix)
                prefix = message.content[:prefix_length]

            return commands.when_mentioned_or(prefix)(self, message)

        except (AttributeError, PrefixNotFound):
            return commands.when_mentioned_or(self.DEFAULT_PREFIX)(self, message)

    # TODO Add caching
    async def get_guild_prefix(self, guild_id: int = None) -> str:
        """
        Using a cached property fetch prefixes
        for a guild and return em.

        Parameters
        ----------
        guild_id : int
            The guild we want prefixes for

        Returns
        -------
        str
            The prefix

        Raises
        ------
        PrefixNotFound
            We failed to find and
            return a valid prefix
        """
        prefix = self.db.config.find(guild_id)

        if not prefix:
            raise PrefixNotFound

        return prefix

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send("Sorry. This command is disabled and cannot be used.")
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                print(f"In {ctx.command.qualified_name}:", file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f"{original.__class__.__name__}: {original}", file=sys.stderr)
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(error)

    async def on_guild_join(self, guild):
        if guild.id in self.blacklist.guilds:
            await guild.leave()

    async def process_commands(self, message):
        ctx = await self.get_context(message)

        if ctx.command is None:
            return

        if ctx.author.id in self.blacklist.users:
            return

        if ctx.guild.id is not None and ctx.guild.id in self.blacklist.guilds:
            return

        await self.invoke(ctx)

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)
