from typing import Union

try:
    from discord import abc
    from discord.ext import commands
except ModuleNotFoundError:
    from discord import abc
    from discord.ext import commands

from bot_base.wraps.meta import Meta


class WrappedChannel(Meta, abc.GuildChannel, abc.PrivateChannel):  # noqa
    """Wraps discord.TextChannel for ease of stuff"""

    @classmethod
    async def convert(cls, ctx, argument: str) -> "WrappedChannel":
        channel: Union[
            abc.GuildChannel, abc.PrivateChannel
        ] = await commands.TextChannelConverter().convert(ctx=ctx, argument=argument)
        return cls(channel, ctx.bot)

    def __getattr__(self, item):
        return getattr(self._wrapped_item, item)
