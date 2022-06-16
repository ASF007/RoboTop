from typing import TYPE_CHECKING

from discord.ext import commands

from bot_base.wraps import Meta

if TYPE_CHECKING:
    from bot_base import BotBase


class BotContext(commands.Context, Meta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bot: "BotBase" = self.bot
        self._wrapped_bot = bot

        self.message = bot.get_wrapped_message(self.message)
