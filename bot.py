import logging
import os

<<<<<<< HEAD
import discord
=======
>>>>>>> 45ff7a15c916b99d44bf5a2b208b645e4e3d72ba
from bot_base import BotBase
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


@bot.command()
async def ping(ctx):
    await ctx.send_basic_embed("Pong!")

bot.run(os.environ["TOKEN"])
