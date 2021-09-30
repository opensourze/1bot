# This file contains the customised help command

import discord
from discord.ext.commands import MinimalHelpCommand


class CustomHelpCommand(MinimalHelpCommand):
    def __init__(self, buttons):
        super().__init__()
        self.buttons = buttons

    async def send_bot_help(self, mapping):
        destination = self.get_destination()

        embed = discord.Embed(title="1Bot Commands", color=0xFF6600)

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

        embed = discord.Embed(title=f"{cog.qualified_name} Commands", color=0xFF6600)
        embed.set_footer(
            text=f"Run `{self.clean_prefix}help` followed by a command name for more info on that command."
        )

        cmd_list = []

        for c in cog.get_commands():
            if not c.hidden:
                cmd_list.append(
                    f"`{self.get_command_signature(c)}`\n{c.brief or c.help}"
                )

        embed.description = "\n\n".join(cmd_list)

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
            embed.add_field(name="Aliases", value=", ".join(aliases), inline=False)

        await destination.send(embed=embed)
