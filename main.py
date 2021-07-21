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


class CustomHelpCommand(commands.MinimalHelpCommand):
    info_btns = create_actionrow(
        *[
            create_button(
                style=ButtonStyle.URL,
                label="Add bot",
                emoji="➕",
                url="https://dsc.gg/1bot",
            ),
            create_button(
                style=ButtonStyle.URL,
                label="Command list",
                emoji="ℹ️",
                url="https://1bot.netlify.app/commands",
            ),
            create_button(
                style=ButtonStyle.URL,
                label="Join server",
                url="https://discord.gg/4yA6XkfnwR",
            ),
        ]
    )

    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(
                title="1Bot Commands", description=page, color=0xFF6600
            )
            embed.set_author(name="1Bot", icon_url=client.user.avatar_url)

            await destination.send(embed=embed, components=[self.info_btns])


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
    with suppress(AttributeError):
        if ctx.command.has_error_handler():
            return  # Exit if command has error handler
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
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(
            f":x: Member not found. Member arguments must have the exact name of the member including capitalisation, or you can just ping the member."
        )
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
    # Send slash command errors to normal command error handler
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
