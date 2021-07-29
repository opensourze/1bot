print("Bot written by @opensourze")

import os
from asyncio import sleep
from contextlib import suppress
from itertools import cycle

import discord
import dotenv
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button

dotenv.load_dotenv()


client = commands.AutoShardedBot(
    command_prefix=commands.when_mentioned_or(*["1 ", "1"]),
    case_insensitive=True,
    help_command=None,
)
slash = SlashCommand(client, sync_commands=True, delete_from_unused_guilds=True)


@client.event
async def on_ready():
    print("-----\nThe bot is now online")
    print(f"{len(client.guilds)} servers\n-----")


async def change_status():
    statuses = cycle(
        ["1 help | you can run my commands in DMs too!", "1 help | 1bot.netlify.app"]
    )

    while not client.is_closed():
        await client.change_presence(activity=discord.Game(name=next(statuses)))
        await sleep(7)


client.loop.create_task(change_status())

error_btns = create_actionrow(
    *[
        create_button(
            style=ButtonStyle.URL,
            url=f"https://opensourze.github.io/1bot/commands",
            label="Command list",
        ),
        create_button(
            style=ButtonStyle.URL,
            url=f"https://discord.gg/4yA6XkfnwR",
            label="Support server",
        ),
    ]
)


@client.event
async def on_command_error(ctx, error):  # Error handlers
    with suppress(AttributeError):
        if ctx.command.has_error_handler():
            return  # Exit if command has error handler
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send(
            ":x: I don't have enough permissions to run this command!\n"
            + "Missing permissions: "
            + f"`{', '.join(error.missing_perms)}`",
            components=[error_btns],
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
            ":x: You've missed one or more required options.\n"
            + "Check the command's help for what options you should provide.",
            components=[error_btns],
        )
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send(":x: I don't think that channel exists!")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(
            f":x: Member not found. Member options must have the exact name of the member including capitalisation, or you can just ping the member."
        )
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f":x: Whoa, slow down. This command is on cooldown, try again in {round(error.retry_after)} seconds."
        )
    elif isinstance(error, commands.BadArgument):
        await ctx.send(":x: Invalid option.", components=[error_btns])
    elif not isinstance(error, commands.CommandNotFound):
        print(error)


@client.event
async def on_slash_command_error(ctx, error):
    # Send slash command errors to normal command error handler
    await on_command_error(ctx, error)


@client.event
async def on_message(message):
    if (
        message.content == f"<@!{client.user.id}>"
        or message.content == f"<@{client.user.id}>"
    ):
        await message.channel.send(
            "My prefix is `1`. You can add a space after it, but it's optional."
        )
    else:
        await client.process_commands(message)


info_btns = create_actionrow(
    *[
        create_button(
            style=ButtonStyle.URL,
            label="Command list",
            emoji="ℹ️",
            url="https://opensourze.github.io/1bot/commands",
        ),
        create_button(
            style=ButtonStyle.URL,
            label="Join the support server",
            url="https://discord.gg/4yA6XkfnwR",
        ),
    ]
)

# Help command
@client.command()
async def help(ctx, *args):
    await ctx.send(
        "**My prefix is `1`**.\n"
        + "You can add a space after the 1 if you want to, but it is completely optional.",
        components=[info_btns],
    )


# Suggest command
@client.command(help="Create a suggestion for the bot")
@commands.cooldown(1, 10, commands.BucketType.user)
async def suggest(ctx, *, suggestion):
    # Get 1Bot support server suggestions channel
    channel = client.get_channel(862697260164055082)

    embed = discord.Embed(title="Suggestion", description=suggestion, color=0xFF6600)
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

    message = await channel.send(embed=embed)
    await ctx.send(
        ":white_check_mark: Your suggestion has been submitted to " + channel.mention
    )
    await message.add_reaction("✅")
    await message.add_reaction("❌")


@slash.slash(name="suggest", description="Create a suggestion for the bot")
@commands.cooldown(1, 10, commands.BucketType.user)
async def suggest_slash(ctx: SlashContext, suggestion):
    await suggest(ctx, suggestion=suggestion)


@client.command(hidden=True, aliases=["stop", "close", "exit"])
@commands.is_owner()
async def logout(ctx):
    await ctx.send(":exclamation: Logging out")
    await client.close()


# Loop through all files in cogs directory and load them
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")


client.run(os.environ["TOKEN"])
