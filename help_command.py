# This file contains the customised help command

import discord
from discord.ext.commands import MinimalHelpCommand

main_colour = 0xFF7000


class CustomHelpCommand(MinimalHelpCommand):
    def __init__(self, buttons):
        super().__init__()
        self.buttons = buttons

    async def send_bot_help(self, mapping):
        destination = self.get_destination()

        embed = discord.Embed(title="1Bot Commands", colour=main_colour)

        for cog, commands in mapping.items():
            command_signatures = [
                self.get_command_signature(c)
                for c in commands
                if "help" not in self.get_command_signature(c) and not c.hidden
            ]
            if command_signatures and "Jishaku" not in cog.qualified_name:
                embed.add_field(
                    name=f"{cog.emoji} {cog.qualified_name}",
                    value=cog.description
                    + f"\nRun `{self.clean_prefix}help {cog.qualified_name.lower()}`\n",
                    inline=False,
                )

        await destination.send(embed=embed, components=[self.buttons])

    async def send_cog_help(self, cog):
        destination = self.get_destination()

        embed = discord.Embed(
            title=f"{cog.qualified_name} Commands", colour=main_colour
        )
        embed.add_field(
            name="Commands are formatted in this manner:",
            value=f"{self.clean_prefix}command <Required option> [Optional option=Default value]\n\n",
            inline=False,
        )
        embed.set_footer(
            text=f"Run {self.clean_prefix}help <command> for more info on that command."
        )

        cmd_list = []

        for c in cog.get_commands():
            if not c.hidden:
                cmd_list.append(
                    f"`{self.get_command_signature(c).strip()}`: {c.brief or c.help}"
                )

        embed.description = "\n\n".join(cmd_list)

        await destination.send(embed=embed, components=[self.buttons])

    async def send_command_help(self, command):
        destination = self.get_destination()

        embed = discord.Embed(
            title=self.get_command_signature(command),
            colour=main_colour,
        )
        embed.add_field(name="Command description", value=command.help)

        aliases = command.aliases
        if aliases:
            embed.add_field(
                name="Aliases",
                value="You can also use this command as:\n" + ", ".join(aliases),
                inline=False,
            )

        await destination.send(embed=embed)
