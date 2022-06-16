import discord
from discord.ext import commands

from bot_base.wraps import Meta


class WrappedThread(Meta, discord.Thread):
    @classmethod
    async def convert(cls, ctx, argument: str) -> "WrappedThread":
        _meta: discord.Thread = await commands.ThreadConverter().convert(
            ctx=ctx, argument=argument
        )
        return cls(_meta, ctx.bot)

    def __getattr__(self, item):
        return getattr(self._wrapped_item, item)
