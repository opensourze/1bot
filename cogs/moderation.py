import asyncio
from contextlib import suppress
from os import environ

import discord
import dotenv
from bson.objectid import ObjectId, InvalidId
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from pymongo import MongoClient

dotenv.load_dotenv()

cluster = MongoClient(environ["MONGO_URL"])
warns = cluster["1bot"]["warns"]
mute_db = cluster["1bot"]["muted"]


class Moderation(commands.Cog, description="All the moderation commands you need."):
    def __init__(self, client):
        self.client = client
        self.emoji = "<:moderation:885461924777693184>"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        muted_role = discord.utils.get(channel.guild.roles[::-1], name="Muted")

        if muted_role:
            await channel.set_permissions(muted_role, send_messages=False, speak=False)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if mute_db.find_one({"user": member.id, "guild": member.guild.id}):
            muted_role = discord.utils.get(member.guild.roles[::-1], name="Muted")

            await member.add_roles(muted_role)

    # Warn command
    @commands.command(help="Warn a member")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def warn(self, ctx, member: commands.MemberConverter, *, reason=None):
        if not reason:
            await ctx.send(
                "❌ You need to provide the reason for the warning.\n"
                + "Run the command again with the reason to warn the member."
            )
            return

        if len(reason) > 970:
            await ctx.send(
                "❌ The reason is too long. Please run the command again with a shorter reason."
            )

        if member == ctx.author:
            await ctx.send("❌ You can't warn yourself!")
            return
        elif member.id == self.client.user.id:
            await ctx.send("❌ I can't warn myself!")
            return
        elif member.guild_permissions.administrator:
            await ctx.send("❌ I can't warn an administrator.")
            return

        with suppress(AttributeError):
            await ctx.trigger_typing()

        inserted_warn = warns.insert_one(
            {
                "user": member.id,
                "guild": ctx.guild.id,
                "moderator": ctx.author.id,
                "reason": reason,
            }
        )

        warn_id = str(inserted_warn.inserted_id)

        with suppress(discord.HTTPException):
            await member.send(
                embed=discord.Embed(
                    title=f"Warned in {ctx.guild.name}",
                    description=f"You have been warned.",
                    color=0xFF6600,
                ).add_field(name="Reason", value=reason)
            )

        warned_embed = discord.Embed(
            title="✅ Member warned",
            description=f"{member.mention} has been warned by {ctx.author.mention}",
            color=0xFF6600,
        )
        warned_embed.add_field(name="Reason", value=reason)
        warned_embed.add_field(name="Unique warning ID", value=warn_id)

        await ctx.send(embed=warned_embed)

    @cog_ext.cog_slash(
        name="warn",
        description="Warn a member",
        options=[
            create_option(
                name="member",
                description="The member to warn",
                option_type=6,
                required=True,
            ),
            create_option(
                name="reason",
                description="Why do you want to warn this member?",
                option_type=3,
                required=True,
            ),
        ],
    )
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def warn_slash(self, ctx, member, reason):
        await self.warn(ctx, member, reason=reason)

    # Warnings command
    @commands.command(help="View the warnings for a member", aliases=["warns"])
    @commands.guild_only()
    async def warnings(self, ctx, *, member: commands.MemberConverter = None):
        member = member or ctx.author

        with suppress(AttributeError):
            await ctx.trigger_typing()

        warn_filter = {"user": member.id, "guild": ctx.guild.id}

        warn_count = warns.count_documents(warn_filter)

        embed = discord.Embed(
            title=f"Warnings for {member}",
            description=f"This member has **{warn_count}** warnings in total.\n"
            + f"Showing max 15 warnings.",
            color=0xFF6600,
        )

        warnings = warns.find(warn_filter)

        i = 0
        for warn in warnings:
            i += 1

            embed.add_field(
                name=f"Warn ID: {warn['_id']}",
                value=f"<@!{warn['moderator']}>: {warn['reason']}",
                inline=False,
            )

            if i == 15:
                break

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="warnings",
        description="View the warnings for a member",
        options=[
            create_option(
                name="member",
                description="The member to view warnings for",
                option_type=6,
                required=True,
            )
        ],
    )
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def warns_slash(self, ctx, member):
        await self.warnings(ctx, member=member)

    # Unwarn/Delwarn command
    @commands.command(
        help="Delete a warning from a member with the warning ID",
        brief="Delete a warning from a user",
        aliases=["unwarn"],
    )
    @commands.has_permissions(manage_messages=True)
    async def delwarn(
        self, ctx, warning_id: str = None, *, member: commands.MemberConverter = None
    ):
        error_msg = "❌ You need to provide the unique warning ID (which can be found with the `warnings` command, or when you warn the user) and then the member to delete the warning from.\n\nExample:\n`delwarn 613a03ec848e6bd3a5e5eca8 @member`"

        if warning_id is None or member is None:
            await ctx.send(error_msg)
            return

        try:
            warn_id = ObjectId(warning_id)
        except InvalidId:
            await ctx.send(
                "❌ Invalid warning ID. The ID is provided after you warn the user. You can also get it with the `warns` command."
            )
            return

        result = warns.find_one(
            {
                "user": member.id,
                "guild": ctx.guild.id,
                "_id": warn_id,
            }
        )

        if not result:
            await ctx.send(
                f"❌ Couldn't find a warning for {member.username} with that ID."
            )
        else:
            with suppress(AttributeError):
                await ctx.trigger_typing()

            warns.delete_one(result)

            await ctx.send(
                embed=discord.Embed(
                    title="✅ Warning deleted",
                    color=0xFF6600,
                    description=f"Warning for {member.mention} with reason `{result['reason']}` has been deleted.",
                )
            )

    @cog_ext.cog_slash(
        name="delwarn",
        description="Delete a warning from a member",
        options=[
            create_option(
                name="warning_id",
                description="The unique warning ID to delete. Can be found with the 'warnings' command",
                option_type=3,
                required=True,
            ),
            create_option(
                name="member",
                description="The member to delete the warning from",
                option_type=6,
                required=True,
            ),
        ],
    )
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def unwarn_slash(self, ctx, warning_id, member):
        await self.delwarn(ctx, warning_id=warning_id, member=member)

    # Clear warns command
    @commands.command(help="Delete all warnings for a member")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def clearwarns(self, ctx, *, member: commands.MemberConverter):
        with suppress(AttributeError):
            await ctx.trigger_typing()

        deleted = warns.delete_many({"user": member.id, "guild": ctx.guild.id})

        await ctx.send(f"✅ Deleted {deleted.deleted_count} warnings for {str(member)}.")

    @cog_ext.cog_slash(
        name="clearwarns",
        description="Delete all warnings for a member",
        options=[
            create_option(
                name="member",
                description="The member to delete warnings for",
                option_type=6,
                required=True,
            )
        ],
    )
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def clearwarns_slash(self, ctx, member):
        await self.clearwarns(ctx, member=member)

    # Nickname command
    @commands.command(help="Change someone's nickname", aliases=["nick"])
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nickname(
        self, ctx, member: commands.MemberConverter, *, nickname: str = None
    ):
        if nickname:
            if len(nickname) > 32:
                await ctx.send(
                    "❌ Nickname is too long! Nicknames must be lesser than 32 characters in length."
                )
                return
        try:
            await member.edit(nick=nickname)
            await ctx.send(f"✅ `{member}`'s nickname has been set to `{nickname}`.")
        except discord.Forbidden:
            await ctx.send(
                "❌ I don't have permission to change that user's nickname.\n"
                + "They might have a higher role than me, or they are the owner."
            )

    @cog_ext.cog_slash(
        name="nickname",
        description="Change someone's nickname",
        options=[
            create_option(
                name="member",
                description="The member whose nickname you want to change.",
                required=True,
                option_type=6,
            ),
            create_option(
                name="nickname",
                description="The nickname you want to change the member to. Leave blank to remove the nickname",
                required=False,
                option_type=3,
            ),
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nickname_slash(self, ctx: SlashContext, member, nickname: str = None):
        await self.nickname(ctx, member, nickname=nickname)

    # Role commands
    @commands.group(invoke_without_command=True, help="Create or delete roles")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(self, ctx):
        embed = discord.Embed(
            title="Role commands",
            description="Run `1 role c {rolename}` to create a role with the provided name.\n"
            + "Run `1 role a {member} {role}` to add the role to the provided member.\n"
            + "Run `1 role d {role}` to delete the role.\n"
            + "Run `1 role r {member} {role}` to remove the role from the member.",
            color=0xFF6600,
        )
        embed.add_field(
            name="PS:",
            value="You can type the name of the role (the exact name, with capitalisation) to provide it as an option, or just @mention it. If you have developer mode on, you can also use the role's ID.",
        )
        embed.set_footer(text="Don't include the brackets while running commands!")

        await ctx.send(embed=embed)

    @role.command(help="Create a role", aliases=["c"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def create(self, ctx, *, name: str):
        await ctx.guild.create_role(name=name)
        await ctx.send(f"✅ Role `{name}` has been created")

    @role.command(help="Delete a role", aliases=["d"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def delete(self, ctx, *, role: commands.RoleConverter):
        await role.delete()
        await ctx.send(f"✅ Role `{role.name}` has been deleted")

    @role.command(help="Add a role to a member", aliases=["a"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def add(
        self, ctx, member: commands.MemberConverter, *, role: commands.RoleConverter
    ):
        await member.add_roles(role)
        await ctx.send(f"✅ Role `{role}` has been added to `{member.name}`.")

    @role.command(help="Remove a role from a member", aliases=["r"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def remove(
        self, ctx, member: commands.MemberConverter, *, role: commands.RoleConverter
    ):
        await member.remove_roles(role)
        await ctx.send(f"✅ Role `{role}` has been removed from `{member.name}`.")

    @cog_ext.cog_subcommand(
        base="role",
        name="create",
        description="Create a new role",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_create_slash(self, ctx: SlashContext, name):
        await self.create(ctx, name=name)

    @cog_ext.cog_subcommand(
        base="role",
        name="delete",
        description="Delete a role",
        options=[
            create_option(
                name="role",
                description="The role you want to delete",
                required=True,
                option_type=8,
            )
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_delete_slash(self, ctx: SlashContext, role):
        await self.delete(ctx, role=role)

    @cog_ext.cog_subcommand(
        base="role",
        name="add",
        description="Add a role to a member",
        options=[
            create_option(
                name="member",
                description="The member you want to add the role to",
                required=True,
                option_type=6,
            ),
            create_option(
                name="role",
                description="The role you want to add",
                required=True,
                option_type=8,
            ),
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_add_slash(self, ctx: SlashContext, member, role):
        await self.add(ctx, member, role=role)

    @cog_ext.cog_subcommand(
        base="role",
        name="remove",
        description="Remove a role from a member",
        options=[
            create_option(
                name="member",
                description="The member you want to remove the role from",
                required=True,
                option_type=6,
            ),
            create_option(
                name="role",
                description="The role you want to remove",
                required=True,
                option_type=8,
            ),
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_remove_slash(self, ctx: SlashContext, member, role):
        await self.remove(ctx, member, role=role)

    # Purge/Clear command
    @commands.command(
        help="Clear multiple messages at once (deletes 5 messages by default)",
        brief="Clear many messages at once",
        aliases=["purge"],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 5):
        await ctx.channel.purge(limit=amount + 1)

    @cog_ext.cog_slash(
        name="clear",
        description="Clear multiple messages at once",
        options=[
            create_option(
                name="amount",
                description="Number of messages to delete (default = 5)",
                required=False,
                option_type=4,
            )
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear_slash(self, ctx: SlashContext, amount: int = 5):
        await self.clear(ctx, amount=amount - 1)
        await ctx.send(f"✅ I have cleared {amount} messages", delete_after=2)

    # Nuke/clear channel command
    @commands.command(help="Clear a channel", aliases=["clearall", "clearchannel"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def nuke(self, ctx, *, channel: discord.TextChannel = None):
        with suppress(discord.NotFound):
            channel = channel or ctx.channel

            msg = await ctx.send(
                "**This command will clear everything in the channel!**\n\nThe channel will be completely emptied.\n**Are you sure you want to do this?**"
            )
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")

            def check(reaction, user):
                return (
                    user == ctx.author
                    and str(reaction.emoji) in ["✅", "❌"]
                    and reaction.message.id == msg.id
                )

            try:
                reaction, user = await self.client.wait_for(
                    "reaction_add", check=check, timeout=20
                )
                if reaction.emoji == "❌":
                    await ctx.send("❗ Cancelling the nuke.")
                    return
                if reaction.emoji == "✅":
                    await channel.purge(limit=None)

                await ctx.send(f"✅ Cleared {channel.mention}", delete_after=2)
            except asyncio.TimeoutError:
                await ctx.send("❌ You didn't react in time, cancelling the nuke.")

    @cog_ext.cog_slash(
        name="clearchannel",
        description="Clear a channel",
        options=[
            create_option(
                name="channel",
                description="The channel you want to clear",
                required=True,
                option_type=7,
            )
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def nuke_slash(self, ctx: SlashContext, channel: discord.TextChannel):
        await self.nuke(ctx, channel=channel)

    # Slowmode command
    @commands.command(
        help="Set slowmode for the current channel", aliases=["slow", "sm"]
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        if seconds < 0:
            await ctx.send("❌ Slowmode must be a positive number")
            return
        elif seconds > 21600:
            await ctx.send("❌ Slowmode must be less than 21600 seconds (6 hours)")
        else:
            await ctx.channel.edit(slowmode_delay=seconds)

        await ctx.send(f"✅ Slowmode set to {seconds} seconds")

    @cog_ext.cog_slash(
        name="slowmode", description="Set slowmode for the current channel"
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode_slash(self, ctx: SlashContext, seconds: int):
        await self.slowmode(ctx, seconds=seconds)

    # This function returns False if the bot cannot mute the member
    async def mute_checker(self, ctx, bot_role, member, muted_role):
        if member == ctx.author:
            await ctx.send("❌ You can't mute yourself!")
            return False

        if member == self.client.user:
            await ctx.send("❌ I can't mute myself!")
            return False

        if bot_role <= member.top_role:
            await ctx.send(
                "❌ The user has a higher role or the same top role as mine.\n"
                + "Please move my role higher!"
            )
            return False

        if not muted_role:
            await ctx.send(
                ":information_source: Couldn't find a Muted role in this server. Creating a new one..."
            )
            muted_role = await ctx.guild.create_role(name="Muted", color=0x919191)

            for channel in ctx.guild.channels:
                await channel.set_permissions(
                    muted_role, send_messages=False, speak=False
                )

        if bot_role <= muted_role:
            await ctx.send(
                "❌ My role is too low. I can only mute users if my role is higher than the Muted role!"
            )
            return False

    # Mute command
    @commands.command(
        help="Remove the permission for a member to send messages or speaking on voice",
        brief="Mute a member",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: commands.MemberConverter, *, reason=None):
        muted_role = discord.utils.get(ctx.guild.roles[::-1], name="Muted")

        if (
            await self.mute_checker(ctx, ctx.guild.me.top_role, member, muted_role)
            == False
        ):
            return

        await member.add_roles(muted_role, reason=reason)

        existing_mute = mute_db.find_one({"user": member.id, "guild": ctx.guild.id})
        if not existing_mute:
            mute_db.insert_one({"user": member.id, "guild": ctx.guild.id})

        embed = discord.Embed(
            title="✅ Member muted",
            color=0xFF6600,
            description=f"{member.mention} was muted by {ctx.author.mention}",
        ).add_field(name="Reason", value=reason)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="mute",
        description="Disallow a member from sending messages or speaking",
        options=[
            create_option(
                name="member",
                description="The member to mute",
                required=True,
                option_type=6,
            )
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute_slash(self, ctx: SlashContext, member, reason=None):
        await self.mute(ctx, member, reason=reason)

    # tempmute command
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}

    invalid_duration_msg = (
        "❌ **Invalid duration**! Here are some examples:\n\n"
        + '`1tempmute @Big Wumpus 2d Spam`- 2 days, with reason "Spam"\n'
        + "`1 tmute Wumpus 1h`- 1 hour without any reason\n"
        + "`1tempmute Wumpus 20m`- 20 minutes without any reason\n"
        + "\nYou can also use `s` for seconds."
    )

    async def time2seconds(self, send, time):
        try:
            return int(time[:-1]) * self.time_convert[time[-1]]
        except:
            await send(self.invalid_duration_msg)
            return False

    @commands.command(help="Temporarily mute a member", aliases=["tmute"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def tempmute(
        self,
        ctx,
        member: commands.MemberConverter,
        duration: str,
        *,
        reason=None,
    ):
        unit_tuple = tuple([unit for unit in self.time_convert.keys()])
        sleep_duration = await self.time2seconds(ctx.send, duration.lower())
        if sleep_duration is False:
            return

        # If duration does not end with one of the units or is not a number, send an error
        if not duration.lower().endswith(unit_tuple) or not duration[0].isdigit():
            await ctx.send(self.invalid_duration_msg)
            return

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if (
            await self.mute_checker(ctx, ctx.guild.me.top_role, member, muted_role)
            == False
        ):
            return

        await member.add_roles(muted_role, reason=reason)

        existing_mute = mute_db.find_one({"user": member.id, "guild": ctx.guild.id})
        if not existing_mute:
            mute_db.insert_one({"user": member.id, "guild": ctx.guild.id})

        embed = discord.Embed(
            title="✅ Member muted",
            color=0xFF6600,
            description=f"{member.mention} was temporarily muted by {ctx.author.mention}",
        )
        embed.add_field(name="Reason", value=reason)
        if not duration[-1].isalpha():
            embed.add_field(name="Auto-unmute after", value=str(duration) + " seconds")
        else:
            embed.add_field(name="Auto-unmute after", value=duration)

        await ctx.send(embed=embed)

        await asyncio.sleep(sleep_duration)
        await member.remove_roles(muted_role, reason=reason)

        mute_db.delete_one({"user": member.id, "guild": ctx.guild.id})

    @cog_ext.cog_slash(
        name="tempmute",
        description="Temporarily mute a member",
        options=[
            create_option(
                name="member",
                description="The member to tempmute",
                required=True,
                option_type=6,
            ),
            create_option(
                name="duration",
                description="The duration of the mute",
                required=True,
                option_type=3,
            ),
            create_option(
                name="reason",
                description="The reason for the mute (optional)",
                required=False,
                option_type=3,
            ),
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def tempmute_slash(self, ctx: SlashContext, member, duration, reason=None):
        await self.tempmute(ctx, member, duration, reason=reason)

    # Unmute command
    @commands.command(help="Unmute a member")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, *, member: commands.MemberConverter):
        deleted = mute_db.find_one_and_delete(
            {"user": member.id, "guild": ctx.guild.id}
        )

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if muted_role not in member.roles and not deleted:
            await ctx.send("❌ That member isn't muted!")
            return
        elif ctx.guild.me.top_role <= muted_role:
            await ctx.send(
                "❌ My role is too low. I can only mute users if my role is higher than the Muted role!"
            )
            return
        elif ctx.guild.me.top_role <= member.top_role:
            await ctx.send(
                "❌ The user has a higher role or the same top role as mine.\n"
                + "Please move my role higher!"
            )
            return

        await member.remove_roles(muted_role)

        embed = discord.Embed(
            title="✅ Member unmuted",
            color=0xFF6600,
            description=f"{member.mention} was unmuted by {ctx.author.mention}",
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="unmute",
        description="Unmute a member",
        options=[
            create_option(
                name="member",
                description="The member to unmute",
                required=True,
                option_type=6,
            )
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute_slash(self, ctx: SlashContext, member):
        await self.unmute(ctx, member=member)

    # Kick command
    @commands.command(
        help="Kick a member by mention/ID/username/nickname, optional reason",
        brief="Kick a member",
    )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: commands.MemberConverter, *, reason=None):
        if member == ctx.author:
            await ctx.send("❌ You can't kick yourself!")
            return
        elif member.id == self.client.user.id:
            await ctx.send("❌ I can't kick myself!")
            return
        elif ctx.guild.me.top_role <= member.top_role:
            await ctx.send(
                "❌ The user has a higher role or the same top role as mine.\n"
                + "Please move my role higher!"
            )
            return

        try:
            await member.send(
                f"❗ You were kicked from {ctx.guild.name}. Reason: {reason}"
            )
        except:
            pass
        await ctx.guild.kick(member, reason=reason)

        embed = discord.Embed(
            title="✅ Member kicked",
            color=0xFF6600,
            description=f"{member.mention} was kicked by {ctx.author.mention}",
        ).add_field(name="Reason", value=reason)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="kick",
        description="Kick a member from the server",
        options=[
            create_option(
                name="member",
                description="The user to kick",
                required=True,
                option_type=6,
            ),
            create_option(
                name="reason",
                description="Why do you want to kick this user? (Optional)",
                required=False,
                option_type=3,
            ),
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick_slash(self, ctx: SlashContext, member, reason=None):
        await self.kick(ctx, member, reason=reason)

    # Ban command
    @commands.command(
        help="Ban a member by mention/ID/username/nickname, optional reason",
        brief="Ban a member",
    )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: commands.MemberConverter, *, reason=None):
        if user == ctx.author:
            await ctx.send("❌ You can't ban yourself!")
            return

        if user == self.client.user:
            await ctx.send("❌ I can't ban myself!")
            return

        with suppress(AttributeError):
            if ctx.guild.me.top_role <= user.top_role:
                await ctx.send(
                    "❌ The user has a higher role or the same top role as mine.\n"
                    + "Please move my role higher!"
                )
                return

        try:
            await user.send(
                f"❗ You were banned from {ctx.guild.name}! Reason: {reason}"
            )
        except:
            pass

        await ctx.guild.ban(user, reason=reason)

        embed = discord.Embed(
            title="✅ Member banned",
            color=0xFF6600,
            description=f"{user.mention} was banned by {ctx.author.mention}",
        ).add_field(name="Reason", value=reason)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="ban",
        description="Ban a member from the server",
        options=[
            create_option(
                name="member",
                description="The user to ban",
                required=True,
                option_type=6,
            ),
            create_option(
                name="reason",
                description="Why do you want to ban this user? (Optional)",
                required=False,
                option_type=3,
            ),
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban_slash(self, ctx: SlashContext, user, reason=None):
        await self.ban(ctx, user, reason=reason)

    # Unban command
    @commands.command(
        help="Unban someone",
    )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user: str):
        banned_users = await ctx.guild.bans()

        try:
            username, user_tag = user.split("#")

            for ban_entry in banned_users:
                banned = ban_entry.user

                if (banned.name, banned.discriminator) == (
                    username,
                    user_tag,
                ):
                    await ctx.guild.unban(banned)
                    await ctx.send(f"✅ Unbanned {banned}")
                    return

        except ValueError:
            await ctx.send(
                "❌ You need to provide the exact username + tag of the banned user to unban them!"
            )
            return

        await ctx.send(f"❌ Couldn't find a ban for {user}")

    @cog_ext.cog_slash(
        name="unban",
        description="Unban someone",
        options=[
            create_option(
                name="user",
                description="The user to unban (username + tag)",
                required=True,
                option_type=3,
            ),
            create_option(
                name="reason",
                description="Why do you want to unban this user? (Optional)",
                required=False,
                option_type=3,
            ),
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban_slash(self, ctx: SlashContext, user: str):
        await self.unban(ctx, user=user)

    # Lockdown command
    @commands.command(
        help="Remove permissions for members to send messages in a channel. Optional: provide a channel to lock (defaults to the channel you are inside)",
        brief="Make a channel read-only",
        aliases=["readonly", "lock"],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lockdown(self, ctx, channel: discord.TextChannel = None):
        # If channel is None, fall back to the channel where the command is being invoked
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await channel.set_permissions(ctx.guild.me, send_messages=True)

        embed = discord.Embed(
            title="✅ Channel locked down",
            color=0xFF6600,
            description=f"{channel.mention} was locked down by {ctx.author.mention}.\n"
            + "Members cannot send messages in the channel now.",
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="lockdown",
        description="Remove permissions for users to send messages to the specified channel",
        options=[
            create_option(
                name="channel",
                description="The channel to lock down (optional, defaults to the channel you are in)",
                required=False,
                option_type=7,
            )
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lockdown_slash(
        self, ctx: SlashContext, channel: discord.TextChannel = None
    ):
        await self.lockdown(ctx, channel=channel)

    # Lockdown Unlock command
    @commands.command(help="Remove a channel from lockdown")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=None)

        embed = discord.Embed(
            title="✅ Channel removed from lockdown",
            color=0xFF6600,
            description=f"{channel.mention} was unlocked by {ctx.author.mention}",
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="unlock",
        description="Remove a channel from lockdown",
        options=[
            create_option(
                name="channel",
                description="The channel to unlock (optional, defaults to the channel you are in)",
                required=False,
                option_type=7,
            )
        ],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock_slash(
        self, ctx: SlashContext, channel: discord.TextChannel = None
    ):
        await self.unlock(ctx, channel=channel)

    # Snipe command
    @commands.command(help="Shows the last deleted message in the current channel")
    @commands.guild_only()
    async def snipe(self, ctx, snipe_channel: discord.TextChannel = None):
        snipe_channel = snipe_channel or ctx.channel

        try:
            content, author, channel, timestamp = self.client.sniped_messages[
                ctx.guild.id
            ][snipe_channel.id]
        except:
            await ctx.send(
                "❌ I couldn't find a deleted message in this channel in my logs."
            )
            return

        embed = discord.Embed(description=content, color=0xFF6600, timestamp=timestamp)
        embed.set_author(name=str(author), icon_url=author.avatar_url)
        embed.add_field(name="Deleted message found in", value=channel.mention)

        if not content:
            embed.title = "Note: This deleted message does not have any text content."

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="snipe",
        description="Find the last deleted message in a channel",
        options=[
            create_option(
                name="channel",
                description="The channel you want to get the deleted message from",
                option_type=7,
                required=False,
            )
        ],
    )
    @commands.guild_only()
    async def snipe_slash(self, ctx: SlashContext, channel=None):
        await self.snipe(ctx, channel)


# Add cog
def setup(client):
    client.add_cog(Moderation(client))
