import logging
import traceback
from contextlib import redirect_stdout
from io import StringIO
from textwrap import indent
from timeit import default_timer

from bot_base import BotBase
from bot_base.context import BotContext


import discord as discord
from discord.ext import commands

log = logging.getLogger(__name__)


class Internal(commands.Cog):
    def __init__(self, bot):
        self.bot: BotBase = bot

    def cleanup_code(self, content):
        """Cleanup code blocks"""
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        return content.strip("` \n")

    def cog_check(self, ctx) -> bool:
        try:
            _exists = self.bot.blacklist
            return True
        except AttributeError:
            return False

    @commands.Cog.listener()
    async def on_ready(self):
        log.info(f"{self.__class__.__name__}: Ready")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def eval(self, ctx: BotContext, *, code: str):
        """
        Evaluates the given code.
        Credits: Hyena Bot

        Example:
        `.eval code`
        """

        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_author(
            name="Evaluate code",
        )
        start = default_timer()
        code = self.cleanup_code(code)
        code = f"async def code():\n{indent(code, '    ')}"
        _global_vars = {"bot": self.bot, "ctx": ctx, "discord": discord}
        buf = StringIO()

        try:
            exec(code, _global_vars)
        except Exception as e:
            embed.description = f"```py\n{e.__class__.__name__}: {e}\n```"
            embed.color = discord.Colour.red()
        else:
            func = _global_vars["code"]
            try:
                with redirect_stdout(buf):
                    resp = await func()
            except Exception as e:
                console = buf.getvalue()
                embed.description = f"```py\n{console}{traceback.format_exc()}\n```"
                embed.color = discord.Colour.red()
            else:
                console = buf.getvalue()
                if not resp and console:
                    embed.description = f"```py\n{console}\n```"
                elif not resp and not console:
                    embed.description = "```<No output>```"
                else:
                    embed.description = f"```py\n{console}{resp}\n```"
            stop = default_timer()

            embed.set_footer(
                text="Evaluated in: {:.5f} seconds".format(stop - start),
            )
            await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def blacklist(self, ctx: BotContext) -> None:
        """Top level blacklist interface"""
        await ctx.send_help(ctx.command)

    @blacklist.group(invoke_without_command=True)
    @commands.is_owner()
    async def add(self, ctx: BotContext) -> None:
        """Add something to the blacklist"""
        await ctx.send_help(ctx.command)

    @add.command(name="person")
    @commands.is_owner()
    async def add_person(
        self, ctx: BotContext, user: discord.Object, *, reason=None
    ) -> None:
        """Add someone to the blacklist"""
        await self.bot.blacklist.add_to_blacklist(
            user.id, reason=reason, is_guild_blacklist=False
        )
        await ctx.send_basic_embed(f"I have added <@{user.id}> to the blacklist.")

    @add.command(name="guild")
    @commands.is_owner()
    async def add_guild(
        self, ctx: BotContext, guild: discord.Object, *, reason=None
    ) -> None:
        await self.bot.blacklist.add_to_blacklist(
            guild.id, reason=reason, is_guild_blacklist=True
        )
        await ctx.send_basic_embed(
            f"I have added the guild `{guild.id}` to the blacklist"
        )

    @blacklist.command()
    @commands.is_owner()
    async def list(self, ctx: BotContext) -> None:
        """List all current blacklists"""
        if self.bot.blacklist.users:
            user_blacklists = "\n".join(f"`{u}`" for u in self.bot.blacklist.users)
        else:
            user_blacklists = "No user's blacklisted."

        if self.bot.blacklist.guilds:
            guild_blacklists = "\n".join(f"`{g}`" for g in self.bot.blacklist.guilds)
        else:
            guild_blacklists = "No guild's blacklisted."

        await ctx.send(
            embed=discord.Embed(
                title="Blacklists",
                description=f"Users:\n{user_blacklists}\n\nGuilds:\n{guild_blacklists}",
            )
        )

    @blacklist.group(invoke_without_command=True)
    @commands.is_owner()
    async def remove(self, ctx: BotContext) -> None:
        """Remove something from the blacklist"""
        await ctx.send_help(ctx.command)

    @remove.command(name="person")
    @commands.is_owner()
    async def remove_person(self, ctx: BotContext, user: discord.Object) -> None:
        """Remove a person from the blacklist.

        Does nothing if they weren't blacklisted.
        """
        await self.bot.blacklist.remove_from_blacklist(
            user.id, is_guild_blacklist=False
        )
        await ctx.send_basic_embed("I have completed that action for you.")

    @remove.command(name="guild")
    @commands.is_owner()
    async def remove_guild(self, ctx: BotContext, guild: discord.Object) -> None:
        """Remove a guild from the blacklist.

        Does nothing if they weren't blacklisted.
        """
        await self.bot.blacklist.remove_from_blacklist(
            guild.id, is_guild_blacklist=True
        )
        await ctx.send_basic_embed("I have completed that action for you.")


async def setup(bot):
    await bot.add_cog(Internal(bot))
