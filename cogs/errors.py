# This file is a cog to handle command errors

from contextlib import suppress

import discord
from discord.ext import commands
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button


class Errors(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.emoji = ""

    @commands.Cog.listener()
    async def on_ready(self):
        self.error_channel = await self.client.fetch_channel(884095331678167111)
        self.error_btns = create_actionrow(
            *[
                create_button(
                    style=ButtonStyle.URL,
                    url=f"https://1bot.netlify.app/commands",
                    label="Command list",
                    emoji=self.client.get_emoji(885086857484992553),
                ),
                create_button(
                    style=ButtonStyle.URL,
                    url=f"https://discord.gg/JGcnKxEPsW",
                    label="Support Server",
                    emoji=self.client.get_emoji(885083336240926730),
                ),
            ]
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return  # Exit if the command is not found
        with suppress(AttributeError):
            if ctx.command.has_error_handler():
                return  # Exit if command has error handler

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                "❌ I don't have enough permissions to complete this command!\n"
                + "Missing permissions: "
                + f"`{', '.join([err.capitalize().replace('_', ' ') for err in error.missing_perms])}`\n\n"
                + "Please add these permissions to my role ('1Bot') in your server settings.",
                components=[self.error_btns],
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "❌ You don't have enough permissions to use this command.\n"
                + "Missing permissions: "
                + f"`{', '.join([err.capitalize().replace('_', ' ') for err in error.missing_perms])}`"
            )
        elif isinstance(error, commands.NotOwner):
            await ctx.send("❌ Only the owner of the bot can use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "❌ You haven't provided enough options.\n"
                + f"Missing option: `{error.param.name}`.",
                components=[self.error_btns],
            )
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(
                "❌ You've passed extra options to the command!\n"
                + "Check the command list to know what options to provide.",
                components=[self.error_btns],
            )
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send(f'❌ I couldn\'t find the channel "{error.argument}".')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f'❌ I couldn\'t find the member "{error.argument}".')
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(f'❌ I couldn\'t find the user "{error.argument}".')
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send(
                f'❌ I couldn\'t find the role "{error.argument}". You need to type the exact name of the role or ping it.'
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"❌ Whoa, slow down. This command is on cooldown, try again in {round(error.retry_after, 2)} seconds."
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.send(
                "❌ You haven't provided the correct types of options, please check the help command or command list.",
                components=[self.error_btns],
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ This command can't be used in direct messages.")
        elif "Forbidden" in str(error):
            await ctx.send(
                "❌ Missing Access error. Possible reasons:\n\n"
                + "1. If I was supposed to perform an action on a *server member*, my roles are too low in the hierarchy. I cannot run this command until you move any of my roles higher than the member's top-most role.\n"
                + "2. If I was supposed to perform an action on a *channel*, I don't have access to that channel because it is private."
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            await ctx.send("❌ You opened a quote but didn't close it!")
        elif isinstance(
            error, commands.UnexpectedQuoteError
        ) or "Expected space after closing quotation" in str(error):
            await ctx.send("❌ You didn't use quotes correctly.")
        elif "cannot identify image file" in str(
            error
        ) or "Unsupported image type" in str(error):
            await ctx.send("❌ I don't think that's a valid image!")
        elif isinstance(error, commands.CheckFailure):
            if "The global check functions for command " in str(error):
                try:
                    await ctx.author.send(
                        "❌ You cannot use 1Bot's commands as you are globally banned."
                    )
                except:
                    pass

        # ERROR REPORTING SYSTEM #
        else:

            error_embed = discord.Embed(
                title="❌ Unhandled error",
                description="Oops, looks like that command returned an unknown error. The error has been automatically reported to the developers in our server and will be fixed soon.\n"
                + "Meanwhile, **do not spam the same command**.",
                colour=0xFF0000,
            )
            error_embed.add_field(
                name="Join our server to track this error",
                value="If you would like to see more about this error and our progress on fixing it, join the server by clicking the button below.",
            )

            try:
                embed = discord.Embed(
                    title="Error",
                    colour=0xFF0000,
                    description=f"Error while invoking command:\n`{ctx.message.content}`",
                ).add_field(name="Error:", value=error)
                embed.set_footer(text=f"User ID: {ctx.author.id}")

            except AttributeError:
                embed = (
                    discord.Embed(
                        title="Error",
                        colour=0xFF0000,
                        description=f"Error while invoking command `/{ctx.name}`",
                    )
                    .add_field(name="Error:", value=error)
                    .set_footer(text=f"User ID: {ctx.author.id}")
                )

            await self.error_channel.send("<@&887918006376747008>", embed=embed)
            await ctx.send(
                embed=error_embed,
                components=[
                    create_actionrow(
                        *[
                            create_button(
                                label="Join the server",
                                style=ButtonStyle.URL,
                                url="https://discord.gg/JGcnKxEPsW",
                            )
                        ]
                    )
                ],
            )

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        await self.on_command_error(ctx, error)


def setup(client):
    client.add_cog(Errors(client))
