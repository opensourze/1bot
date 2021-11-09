# This file contains the client along with most events.

from asyncio import sleep
from itertools import cycle
from os import environ

import discord
from animation import Wait
from chalk import Chalk
from discord.ext import commands
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button
from discord_together import DiscordTogether
from dotenv import load_dotenv

load_dotenv()

from help_command import CustomHelpCommand

# The strings that animate before 1Bot is ready
starting_steps = [
    "Starting 1Bot   ",
    "Starting 1Bot.  ",
    "Starting 1Bot.. ",
    "Starting 1Bot...",
]


class Client(commands.AutoShardedBot):
    def __init__(self):
        # "Starting 1Bot..." animation
        self.starting = Wait(animation=starting_steps)
        self.starting.start()

        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True

        # Initialise AutoShardedBot
        super().__init__(
            command_prefix=["1. ", "1."],
            case_insensitive=True,
            intents=intents,
            owner_ids=[748791790798372964, 856609450236313660],
            allowed_mentions=discord.AllowedMentions(everyone=False),
        )

        """
        The line below makes the help command case insensitive so that you can run 'help fun' or 'help Fun'.
        """
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

    colour = 0xFF7000

    async def on_ready(self):
        self.starting.stop()
        green = Chalk("green")
        print(green(f"{self.user.name} is now ready"), end=None)

        buttons = create_actionrow(
            *[
                create_button(
                    label="Command list",
                    style=ButtonStyle.URL,
                    emoji=self.get_emoji(907549965444849675),
                    url="https://1bot.netlify.app/commands",
                ),
                create_button(
                    label="Support Server",
                    style=ButtonStyle.URL,
                    emoji=self.get_emoji(907550097368301578),
                    url="https://discord.gg/JGcnKxEPsW",
                ),
                create_button(
                    style=ButtonStyle.URL,
                    label="Add me",
                    emoji=self.get_emoji(907549597105278976),
                    url="https://dsc.gg/1bot",
                ),
            ]
        )

        self.help_command = CustomHelpCommand(buttons)
        self.loop.create_task(self.change_status())

        self.dt = await DiscordTogether(environ["TOKEN"])

    # Send prefix when mentioned
    async def on_message(self, message):
        if (
            message.content == f"<@!{self.user.id}>"
            or message.content == f"<@{self.user.id}>"
        ):
            await message.channel.send(
                "My prefix is `1`. You can add a space after it, but it's optional."
            )
        else:
            await self.process_commands(message)

    # Changing status
    async def change_status(self):
        statuses = cycle(
            [
                "1help | You can run my commands in DMs too!",
                "1help | 1bot.netlify.app",
                '1help | Join the official server, "Planet 1Bot" - link in my About Me!',
            ]
        )

        while not self.is_closed():
            await self.change_presence(activity=discord.Game(name=next(statuses)))
            await sleep(10)

    # Store message details when it is deleted

    sniped_messages = {}

    async def on_message_delete(self, message):
        if not message.guild:
            return

        try:
            # Update the guild's dict with the sniped message
            self.sniped_messages[message.guild.id].update(
                {
                    message.channel.id: {
                        "content": message.content,
                        "author": str(message.author),
                        "author_avatar": message.author.avatar_url,
                        "timestamp": message.created_at,
                        "attachments": message.attachments,
                    }
                }
            )
        except KeyError:
            # Creates a new dict for the guild if it isn't stored
            self.sniped_messages[message.guild.id] = {
                message.channel.id: {
                    "content": message.content,
                    "author": str(message.author),
                    "author_avatar": message.author.avatar_url,
                    "timestamp": message.created_at,
                    "attachments": message.attachments,
                }
            }
