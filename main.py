print("Bot written by @opensourze")

import os
from asyncio import sleep
from contextlib import suppress
from itertools import cycle

import discord
import dotenv
from discord.ext import commands
from discord.ext.commands.errors import ExtensionNotLoaded
from discord_slash import SlashCommand
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button

from help_command import CustomHelpCommand

dotenv.load_dotenv()

intents = discord.Intents.default()
intents.guilds = True

client = commands.AutoShardedBot(
    command_prefix=commands.when_mentioned_or(*["1. ", "1."]),
    case_insensitive=True,
    intents=intents,
    help_command=CustomHelpCommand(),
)
client._BotBase__cogs = commands.core._CaseInsensitiveDict()
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
        await sleep(8)


client.loop.create_task(change_status())


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
            url="https://1bot.netlify.app/commands",
        ),
        create_button(
            style=ButtonStyle.URL,
            label="Join the support server",
            url="https://discord.gg/KRjZaV9DP8",
        ),
    ]
)


@client.command(hidden=True, aliases=["refresh"])
@commands.is_owner()
async def reload(ctx):
    msg = await ctx.send("Reloading cogs")

    with suppress(ExtensionNotLoaded):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                client.unload_extension(f"cogs.{filename[:-3]}")

        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                client.load_extension(f"cogs.{filename[:-3]}")

    await msg.edit(content="✅ Reloaded cogs")


# Loop through all files in cogs directory and load them
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")

# Load Jishaku
client.load_extension("jishaku")


client.run(os.environ["TOKEN"])
