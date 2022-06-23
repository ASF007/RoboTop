import logging
import os

import discord
from bot_base import BotBase, context
from bot_base.paginators.disnake_paginator import discordPaginator, PaginationView
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = BotBase(
    command_prefix="t.",
    mongo_url=os.environ["MONGO_URL"],
    mongo_database_name="my_bot",
    load_builtin_commands=True,
    intents = discord.Intents.all()
)


@bot.event
async def on_ready():
    print("I'm up.")


@bot.command()
async def echo(ctx):
    await ctx.message.delete()

    text = await ctx.get_input("What should I say?", timeout=5)

    if not text:
        return await ctx.send("You said nothing!")

    await ctx.send(text)
    await ctx.send(bot.gen_uuid())


@bot.command()
async def ping(ctx):
    d = (("Water#2222", 554), ("Ace#2222", 333))
    x = []
    for i in d:
        fmt = (
            f"**Name:** {i[0]}\n"
            f"**Warn ID:** {i[1]}"
        )
        x.append(fmt)

    pag = discordPaginator(1, x)
    await pag.start(context = ctx)
    

bot.run(os.environ["TOKEN"])
