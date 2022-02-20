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
            command_prefix="1",
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

        # Storing all the buttons needed
        support_btn = create_button(
            label="Support Server",
            style=ButtonStyle.URL,
            emoji=self.get_emoji(907550097368301578),
            url="https://discord.gg/JGcnKxEPsW",
        )
        help_buttons = create_actionrow(
            *[
                create_button(
                    label="Command list",
                    style=ButtonStyle.URL,
                    emoji=self.get_emoji(907549965444849675),
                    url="https://1bot.opensourze.gq/commands",
                ),
                support_btn,
                create_button(
                    style=ButtonStyle.URL,
                    label="Add me",
                    emoji=self.get_emoji(907549597105278976),
                    url="https://dsc.gg/1bot",
                ),
            ]
        )
        self.help_command = CustomHelpCommand(help_buttons)

        self.info_btns = create_actionrow(
            *[
                create_button(
                    style=ButtonStyle.URL,
                    label="Add me",
                    emoji=self.get_emoji(907549597105278976),
                    url="https://dsc.gg/1bot",
                ),
                create_button(
                    style=ButtonStyle.URL,
                    label="Website",
                    emoji=self.get_emoji(907550015063461898),
                    url="https://1bot.opensourze.gq/",
                ),
                support_btn,
                create_button(
                    style=ButtonStyle.URL,
                    label="Upvote",
                    emoji=self.get_emoji(907550047959412736),
                    url="https://top.gg/bot/884080176416309288/vote",
                ),
            ]
        )
        self.error_channel = await self.fetch_channel(884095331678167111)
        self.error_btns = create_actionrow(
            *[
                create_button(
                    style=ButtonStyle.URL,
                    url=f"https://1bot.opensourze.gq/commands",
                    label="Command list",
                    emoji=self.get_emoji(907549965444849675),
                ),
                support_btn,
            ]
        )

        self.loop.create_task(self.change_status())

        self.dt = await DiscordTogether(environ["TOKEN"])

    # Send prefix when mentioned
    async def on_message(self, message):
        if (
            message.content == f"<@!{self.user.id}>"
            or message.content == f"<@{self.user.id}>"
        ):
            embed = discord.Embed(
                description="Hello! Get started by sending `1help`.", colour=self.colour
            )
            embed.add_field(
                name="Support links",
                value="[Command list](https://1bot.opensourze.gq/commands) | [Support server](https://discord.gg/JGcnKxEPsW)",
            )
            embed.set_footer(
                text="The prefix for 1Bot is 1 for all commands. Slash Commands are also fully supported."
            )
            await message.channel.send(embed=embed)
        else:
            await self.process_commands(message)

    # Changing status
    async def change_status(self):
        statuses = cycle(
            [
                "1help | You can run my commands in DMs too!",
                "1help | 1bot.opensourze.gq",
                '1help | Join the official server, "Planet 1Bot" - link in my About Me!',
            ]
        )

        while not self.is_closed():
            await self.change_presence(activity=discord.Game(name=next(statuses)))
            await sleep(10)

    # Store message details when it is deleted

    sniped_messages = {}
    esniped_messages = {}

    def sniped_message_to_dict(self, message):
        return {
            "content": message.content,
            "author": str(message.author),
            "author_avatar": message.author.avatar_url,
            "timestamp": message.created_at,
            "attachments": [
                {"url": a.url, "filename": a.filename} for a in message.attachments
            ],
        }

    async def on_message_delete(self, message):
        if not message.guild:
            return

        try:
            # Update the guild's dict with the sniped message
            self.sniped_messages[message.guild.id].update(
                {message.channel.id: self.sniped_message_to_dict(message)}
            )
        except KeyError:
            # Creates a new dict for the guild if it isn't stored
            self.sniped_messages[message.guild.id] = {
                message.channel.id: self.sniped_message_to_dict(message)
            }

    async def on_message_edit(self, before, after):
        if not before.guild:
            return

        try:
            self.esniped_messages[before.guild.id].update(
                {before.channel.id: self.sniped_message_to_dict(before)}
            )
        except KeyError:
            self.esniped_messages[before.guild.id] = {
                before.channel.id: self.sniped_message_to_dict(before)
            }
