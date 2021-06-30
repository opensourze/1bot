print("Bot written by OpenSourze#1111")

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import os
import dotenv
import platform
from asyncio import sleep
from itertools import cycle

dotenv.load_dotenv()


class CustomHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(title="Commands", description=page, color=0xFF6600)
            embed.set_author(name="I Do Stuff", icon_url=client.user.avatar_url)

            await destination.send(embed=embed)


client = commands.AutoShardedBot(
    command_prefix=commands.when_mentioned_or("_"),
    case_insensitive=True,
    help_command=CustomHelpCommand(),
)
slash = SlashCommand(client, sync_commands=True, delete_from_unused_guilds=True)


@client.event
async def on_ready():
    print("-----\nThe bot is now online")
    print(f"{len(client.guilds)} servers\n-----")


async def change_status():
    statuses = cycle(
        [
            "you can run my commands in DMs too!",
            "_help",
            "I want that verified checkmark.",
        ]
    )

    while not client.is_closed():
        await client.change_presence(activity=discord.Game(name=next(statuses)))
        await sleep(6)


client.loop.create_task(change_status())


@client.event
async def on_command_error(ctx, error):  # Error handlers
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send(
            "Command failed - I don't have enough permissions to run this command!"
        )
    elif isinstance(error, commands.MissingPermissions):

        await ctx.send("You don't have enough permissions to use this command.")
    elif isinstance(error, commands.NotOwner):
        await ctx.send("Only the owner of the bot can use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "You've missed one or more required arguments.\n"
            + "Check the command's help for what arguments you should provide."
        )
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send("I don't think that channel exists!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"Whoa, slow down. This command is on cooldown, try again in {round(error.retry_after)} seconds."
        )
    # else:
    #     print(error)


@client.event
async def on_slash_command_error(ctx, error):
    # Send slash command errors to ext.commands error handler
    await on_command_error(ctx, error)


# Ping command
@client.command(
    help="Tests the bot's latency and displays it in milliseconds",
    brief="Tests the bot's latency",
)
async def ping(ctx):
    await ctx.send(f"Pong! The bot's latency is `{round(client.latency * 1000)}ms`")


# Info command
@client.command(
    help="View the bot's information", brief="View information", aliases=["information"]
)
async def info(ctx):
    info_embed = discord.Embed(title="`I Do Stuff` information", color=0xFF6600)
    info_embed.add_field(
        name="Source code",
        value="View the bot's source code on [GitHub](https://github.com/opensourze/i-do-stuff)",
        inline=False,
    )
    info_embed.add_field(
        name="Creator",
        value="[OpenSourze#1111](https://github.com/opensourze)",
        inline=False,
    )
    info_embed.add_field(
        name="Discord.py version", value=discord.__version__, inline=False
    )
    info_embed.add_field(
        name="Python version", value=platform.python_version(), inline=False
    )
    info_embed.set_thumbnail(
        url="https://cdn.discordapp.com/avatars/848936530617434142/548866771e35e12361e4822b3807e717.png?size=512"
    )
    info_embed.add_field(
        name="Links",
        value="[Invite](https://dsc.gg/i-do-stuff) | [Upvote](https://discordbotlist.com/bots/i-do-stuff/upvote)",
        inline=False,
    )
    await ctx.send(embed=info_embed)


# Upvote command
@client.command(help="Upvote me on DiscordBotList")
async def upvote(ctx):
    await ctx.send(
        "If you like this bot, upvote it on DiscordBotList to help it grow!\n"
        + "You can upvote every 12 hours.\n\n"
        + "https://discordbotlist.com/bots/i-do-stuff/upvote/"
    )


# Suggest command
@client.command(help="Create a suggestion for the bot")
@commands.cooldown(1, 10, commands.BucketType.user)
async def suggest(ctx, *, suggestion):
    me = await client.fetch_user(748791790798372964)

    embed = discord.Embed(title="Suggestion", description=suggestion, color=0xFF6600)
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)

    await me.send(embed=embed)
    await ctx.send("Your suggestion has been submitted to the owner of the bot.")


@client.command(hidden=True, aliases=["stop", "close"])
@commands.is_owner()
async def logout(ctx):
    await ctx.send("Logging out")
    await client.close()


# Slash commands


@slash.slash(name="ping", description="Test the bot's latency")
async def ping_slash(ctx: SlashContext):
    await ping(ctx)


@slash.slash(name="info", description="View the bot's information")
async def info_slash(ctx: SlashContext):
    await info(ctx)


@slash.slash(name="suggest", description="Create a suggestion for the bot")
@commands.cooldown(1, 10, commands.BucketType.user)
async def suggest_slash(ctx: SlashContext, suggestion):
    await suggest(ctx, suggestion=suggestion)


@slash.slash(name="upvote", description="Upvote me on DiscordBotList")
async def upvote_slash(ctx: SlashContext):
    await upvote(ctx)


# Loop through all files in cogs directory and load them
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")


client.run(os.environ["TOKEN"])
