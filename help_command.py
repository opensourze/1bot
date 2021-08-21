import discord
from discord.ext.commands import MinimalHelpCommand
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button


class CustomHelpCommand(MinimalHelpCommand):
    buttons = create_actionrow(
        *[
            create_button(
                label="Command List (recommended)",
                style=ButtonStyle.URL,
                emoji="📃",
                url="https://1bot.netlify.app/commands",
            ),
            create_button(
                label="Join the Support Server",
                style=ButtonStyle.URL,
                url="https://discord.gg/KRjZaV9DP8",
            ),
            create_button(
                style=ButtonStyle.URL,
                label="Add bot",
                emoji="➕",
                url="https://dsc.gg/1bot",
            ),
        ]
    )

    async def send_bot_help(self, mapping):
        destination = self.get_destination()

        embed = discord.Embed(title="1Bot Commands", color=0xFF6600)

        for cog, commands in mapping.items():
            command_signatures = [
                self.get_command_signature(c)
                for c in commands
                if "help" not in self.get_command_signature(c) and not c.hidden
            ]
            if command_signatures:
                embed.add_field(
                    name=cog.qualified_name,
                    value=f"{cog.description}\nRun `1 help {cog.qualified_name.lower()}`",
                    inline=False,
                )

        await destination.send(embed=embed, components=[self.buttons])

    async def send_cog_help(self, cog):
        destination = self.get_destination()

        embed = discord.Embed(
            title=f"{cog.qualified_name} Commands",
            color=0xFF6600,
            description="Run `1 help <command>` for more info on the command.\n\n"
            + "Don't type the brackets while using any commands.\n"
            + "If an option is in <angle brackets>, it is required. If it's in [square brackets], it's optional.\n"
            + "If there is an equal sign (`=`), the text that comes after it is the default value for that option.",
        )

        for c in cog.get_commands():
            if not c.hidden:
                embed.add_field(
                    name=self.get_command_signature(c),
                    value=c.brief or c.help,
                    inline=False,
                )

        await destination.send(embed=embed, components=[self.buttons])

    async def send_command_help(self, command):
        destination = self.get_destination()

        embed = discord.Embed(
            title=self.get_command_signature(command),
            color=0xFF6600,
            description="Don't type the brackets while using commands.\n"
            + "If an option is in <angle brackets>, it is required. If it's in [square brackets], it's optional."
            + "If there is an equal sign (`=`), the text that comes after it is the default value for that option.\n",
        )
        embed.add_field(name="Description", value=command.help)

        aliases = command.aliases
        if aliases:
            embed.add_field(name="Aliases", value=", ".join(aliases))

        await destination.send(embed=embed)
