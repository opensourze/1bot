print("Bot written by OpenSourze#1111")

import os
import platform
from asyncio import sleep
from itertools import cycle

import discord
import dotenv
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

dotenv.load_dotenv()


class CustomHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(
                title="1Bot Commands", description=page, color=0xFF6600
            )
            embed.set_author(name="1Bot", icon_url=client.user.avatar_url)
            embed.add_field(
                name="Helpful links",
                value="[Add bot](https://dsc.gg/1bot)"
                + " | [Official website](https://1bot.netlify.app)"
                + " | [Official server](https://discord.gg/4yA6XkfnwR)",
                inline=False,
            )

            await destination.send(embed=embed)


client = commands.AutoShardedBot(
    command_prefix=commands.when_mentioned_or(*["1 ", "1"]),
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
        ["you can run my commands in DMs too!", "1 help | 1bot.netlify.app"]
    )

    while not client.is_closed():
        await client.change_presence(activity=discord.Game(name=next(statuses)))
        await sleep(7)


client.loop.create_task(change_status())


@client.event
async def on_command_error(ctx, error):  # Error handlers
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send(
            ":x: I don't have enough permissions to run this command!\n"
            + "Missing permissions: "
            + f"`{', '.join(error.missing_perms)}`"
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            ":x: You don't have enough permissions to use this command.\n"
            + "Missing permissions: "
            + f"`{', '.join(error.missing_perms)}`"
        )
    elif isinstance(error, commands.NotOwner):
        await ctx.send(":x: Only the owner of the bot can use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            ":x: You've missed one or more required arguments.\n"
            + "Check the command's help for what arguments you should provide."
        )
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send(":x: I don't think that channel exists!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f":x: Whoa, slow down. This command is on cooldown, try again in {round(error.retry_after)} seconds."
        )
    elif isinstance(error, commands.BadArgument):
        await ctx.send(":x: Invalid argument.")
    elif not isinstance(error, commands.CommandNotFound):
        print(error)


@client.event
async def on_slash_command_error(ctx, error):
    # Send slash command errors to normal commands error handler
    await on_command_error(ctx, error)


@client.event
async def on_message(message):
    if (
        message.content == f"<@!{client.user.id}>"
        or message.content == f"<@{client.user.id}>"
    ):
        await message.channel.send("My prefix is `1`. Optionally add a space after it.")
    else:
        await client.process_commands(message)


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
    info_embed = discord.Embed(title="`1Bot` information", color=0xFF6600)
    info_embed.add_field(
        name="Source code",
        value="View the bot's source code on [GitHub](https://github.com/opensourze/1bot)",
        inline=False,
    )
    info_embed.add_field(
        name="Creator",
        value="[OpenSourze#1111](https://github.com/opensourze)",
        inline=False,
    )
    info_embed.add_field(
        name="Servers", value=f"I'm in {len(client.guilds)} servers as of now"
    )
    info_embed.add_field(name="Bot version", value="0.10.0", inline=False)
    info_embed.add_field(
        name="Discord.py version", value=discord.__version__, inline=False
    )
    info_embed.add_field(
        name="Python version", value=platform.python_version(), inline=False
    )
    info_embed.add_field(
        name="Links",
        value="[Official website](https://1bot.netlify.app)"
        + " | [Add bot](https://dsc.gg/1bot)"
        + " | [Official server](https://discord.gg/4yA6XkfnwR)",
        inline=False,
    )
    info_embed.set_thumbnail(url=client.user.avatar_url)
    await ctx.send(embed=info_embed)


# Upvote command
# @client.command(help="Upvote me on DiscordBotList")
# async def upvote(ctx):
#    await ctx.send(
#        "If you like this bot, upvote it on Top.gg to help it grow!\n"
#        + "You can upvote every 12 hours.\n\n"
#        + "https://top.gg/bot/848936530617434142/vote/"
#    )


# Suggest command
@client.command(help="Create a suggestion for the bot")
@commands.cooldown(1, 10, commands.BucketType.user)
async def suggest(ctx, *, suggestion):
    channel = client.get_channel(862697260164055082)

    embed = discord.Embed(title="Suggestion", description=suggestion, color=0xFF6600)
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

    message = await channel.send(embed=embed)
    await ctx.send(
        ":white_check_mark: Your suggestion has been submitted to " + channel.mention
    )
    await message.add_reaction("✅")
    await message.add_reaction("❌")


# Invite command
@client.command(help="Add the bot to your server", aliases=["addbot"])
async def invite(ctx):
    await ctx.send("https://dsc.gg/1bot")


@client.command(hidden=True, aliases=["stop", "close", "exit"])
@commands.is_owner()
async def logout(ctx):
    await ctx.send(":exclamation: Logging out")
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


@slash.slash(name="invite", description="Add the bot to your server")
async def invite_slash(ctx: SlashContext):
    await ctx.send("https://dsc.gg/1bot")


# @slash.slash(name="upvote", description="Upvote me on DiscordBotList")
# async def upvote_slash(ctx: SlashContext):
#     await upvote(ctx)


# Loop through all files in cogs directory and load them
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")


client.run(os.environ["TOKEN"])
