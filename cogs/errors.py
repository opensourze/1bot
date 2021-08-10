import discord
from discord.ext import commands
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button

error_btns = create_actionrow(
    *[
        create_button(
            style=ButtonStyle.URL,
            url=f"https://1bot.netlify.app/commands",
            label="Command list",
            emoji="ℹ️",
        ),
        create_button(
            style=ButtonStyle.URL,
            url=f"https://discord.gg/4yA6XkfnwR",
            label="Support server",
        ),
    ]
)


class Errors(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if ctx.command.has_error_handler():
            return  # Exit if command has error handler
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                "❌ I don't have enough permissions to complete this command!\n"
                + "Missing permissions: "
                + f"`{', '.join([err.capitalize().replace('_', ' ') for err in error.missing_perms])}`\n\n"
                + "Please add these permissions to my role ('1Bot') in your server settings.",
                components=[error_btns],
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
                "❌ You haven't provided all the required options.\n"
                + "Check the command list to know what options to provide.",
                components=[error_btns],
            )
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(
                "❌ You've passed extra options to the command!\n"
                + "Check the command list to know what options to provide.",
                components=[error_btns],
            )
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("❌ I don't think that channel exists!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                f"❌ Member not found. The member option must have the exact name of the member including capitalisation, or you can just ping the member."
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                f"❌ User not found. The user option must have the exact name + tag of the user including capitalisation, or you can just @mention them if they are in the server. If you have developer mode on, you can also use the user's ID."
            )
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send(
                f"❌ Role not found. The role option must have the exact name of the role including capitalisation, or you can just @mention the role. If you have developer mode on, you can use the role's ID."
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"❌ Whoa, slow down. This command is on cooldown, try again in {round(error.retry_after)} seconds."
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid option.", components=[error_btns])
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ This command can't be used in direct messages.")
        elif "Forbidden" in str(error):
            await ctx.send(
                "❌ I'm unable to complete the command, **my role is probably too low**, or the member you gave me is the **owner/admin**!"
            )
        elif isinstance(error, commands.ExpectedClosingQuoteError):
            await ctx.send("❌ You opened a quote but didn't close it!")
        elif isinstance(
            error, commands.UnexpectedQuoteError
        ) or "Expected space after closing quotation" in str(error):
            await ctx.send("❌ You didn't use quotes correctly.")
        elif "cannot identify image file" in str(error):
            await ctx.send("❌ I don't think that's a valid image!")
        elif "Invalid base64-encoded string" in str(
            error
        ) or "Incorrect padding" in str(error):
            await ctx.send("❌ That base64 code is invalid. Are you sure it's base64?")
        else:
            channel = self.client.get_channel(871032761018896414)
            try:
                embed = discord.Embed(
                    title="Error",
                    color=0xFF0000,
                    description=f"Error while invoking command:\n`{ctx.message.content}`",
                ).add_field(name="Error:", value=error)

                await channel.send("<@&864736371045695519>", embed=embed)
                await ctx.send(
                    "❌ Something went wrong, probably on our side!\n"
                    + "The developers have been notified. We'll fix this as soon as we can!"
                )
            except AttributeError:
                embed.description = f"Error while invoking command:\n`/{ctx.name}"
                embed.add_field(name="Args", value=ctx.args)
                embed.add_field(name="Kwargs", value=ctx.kwargs)
                embed.add_field(name="Error:", value=error)

                await channel.send("<@&864736371045695519>", embed=embed)
                await ctx.send(
                    "❌ Something went wrong, probably on our side!\n"
                    + "The developers have been notified. We'll fix this as soon as we can!"
                )

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        await self.on_command_error(ctx, error)


def setup(client):
    client.add_cog(Errors(client))
