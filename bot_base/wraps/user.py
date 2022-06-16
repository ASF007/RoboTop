import discord
from discord.ext import commands

from bot_base.wraps.meta import Meta


class WrappedUser(Meta, discord.User):
    """Wraps discord.user for ease of stuff"""

    @classmethod
    async def convert(cls, ctx, argument: str) -> "WrappedUser":
        user: discord.User = await commands.UserConverter().convert(
            ctx=ctx, argument=argument
        )
        return cls(user, ctx.bot)

    def __getattr__(self, item):
        return getattr(self._wrapped_item, item)
