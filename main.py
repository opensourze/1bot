import discord
import os
import dotenv
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
dotenv.load_dotenv()

client = commands.Bot(command_prefix="_",
                      case_insensitive=True,
                      activity=discord.Game("_help"))
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    print("Main script is running")


@client.event
async def on_command_error(ctx, error):  # Error handlers
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Command failed - I don't have enough permissions to run this command!")
    elif isinstance(error, commands.MissingPermissions):

        await ctx.send("You don't have enough permissions to use this command.")
    elif isinstance(error, commands.NotOwner):
        await ctx.send("Only the owner of the bot can use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You've missed one or more required arguments. Check the command's help for what arguments you should provide.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Bad Argument error - make sure you've typed your arguments correctly.")
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send("I don't think that channel exists!")


@client.command(help="Tests the bot's latency and displays it in miliseconds")
async def ping(ctx):
    await ctx.send(f"Pong! The bot's latency is `{round(client.latency * 1000)}ms`")


@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension}")


@client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unloaded {extension}")


@client.command(help="Get a link to the bot's source code on GitHub", aliases=["source", "sourcecode"])
async def github(ctx):
    await ctx.send("https://github.com/objectopensource/i-do-stuff-bot\nIf you want to run your own instance of the bot, clone the repository or download it as a .zip and run `main.py.` Feel free to fork the repository.\nThere is a `requirements.txt` file too, so you can install the requirements with `pip install -r requirements.txt`")


# Slash commands


@slash.slash(description="Test the bot's latency", name="ping")
async def ping_slash(ctx: SlashContext):
    await ping(ctx)


@slash.slash(description="View the bot's source code on GitHub")
async def github_slash(ctx: SlashContext):
    await github(ctx)


# Loop through all files in cogs directory and load them
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(os.environ["TOKEN"])
