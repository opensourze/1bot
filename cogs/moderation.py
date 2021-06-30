import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    # Purge/Clear command
    @commands.command(
        help="Clear multiple messages at once (deletes 5 messages by default)",
        brief="Clear many messages at once",
        aliases=["purge"],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount + 1)

    # Mute command
    @commands.command(
        help="Remove the permission for a member to send messages or speaking on voice",
        brief="Mute a member",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: commands.MemberConverter, *, reason=None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if member == ctx.author:
            await ctx.send(":x: You can't mute yourself!")
            return

        if member == self.client.user:
            await ctx.send(":x: I can't mute myself!")
            return

        bot = ctx.guild.get_member(self.client.user.id)
        bot_role = bot.top_role
        if member.top_role >= ctx.author.top_role:
            await ctx.send(
                ":x: The user has a higher role or the same role as your top role.\n"
                + "I can't mute them!"
            )
            return

        if bot_role <= member.top_role:
            await ctx.send(
                ":x: The user has a higher role or the same top role as mine.\n"
                + "Please move my role higher!"
            )
            return

        if bot_role <= muted_role:
            await ctx.send(
                ":x: My role is too low. I can only mute users if my role is higher than the Muted role!"
            )
            return

        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted", color=0xFF0000)

            for channel in ctx.guild.channels:
                await channel.set_permissions(
                    muted_role, send_messages=False, speak=False
                )
                await ctx.send(
                    ":information: New Muted role created. Now muting member..."
                )
                break

        await member.add_roles(muted_role, reason=reason)
        await ctx.send(
            f":white_check_mark: {member.mention} has been muted with the reason: {reason}."
        )

    # Unmute command
    @commands.command(help="Unmute a member")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, *, member: commands.MemberConverter):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(muted_role)
        await ctx.send(f":white_check_mark: {member.mention} has been unmuted")

    # Kick command
    @commands.command(
        help="Kick a member by mention/ID/username/nickname, optional reason",
        brief="Kick a member",
    )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: commands.MemberConverter, *, reason=None):
        try:
            await member.send(
                f":exclamation: You were kicked from {ctx.guild.name}. Reason: {reason}"
            )
        except discord.Forbidden:
            pass
        await ctx.guild.kick(member, reason=reason)
        await ctx.send(f":white_check_mark: Kicked {member.mention}. Reason: {reason}")

    # Ban command
    @commands.command(
        help="Ban a member by mention/ID/username/nickname, optional reason",
        brief="Ban a member",
    )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: commands.UserConverter, *, reason=None):
        try:
            await member.send(
                f":exclamation: You were banned from {ctx.guild.name}! Reason: {reason}"
            )
        except discord.Forbidden:
            pass
        await ctx.guild.ban(member, reason=reason)
        await ctx.send(f":white_check_mark: Banned {member.mention}. Reason: {reason}")

    # Lockdown command
    @commands.command(
        help="Remove permissions for members to send messages in a channel. Optional: provide a channel to lock (defaults to the channel you are inside)",
        brief="Make a channel read-only",
        aliases=["readonly", "lock"],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx, channel: discord.TextChannel = None):
        # If channel is None, fall back to the channel where the command is being invoked
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f":white_check_mark: I have locked down {channel.mention}.")

    # Lockdown Unlock command
    @commands.command(
        help="Remove a channel from lockdown", brief="Remove a channel from lockdown"
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f":white_check_mark: I have unlocked {channel.mention}.")

    # Slash commands

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
    @commands.has_permissions(manage_messages=True)
    async def clear_slash(self, ctx: SlashContext, amount: int = 5):
        await self.clear(ctx, amount=amount - 1)
        await ctx.send(
            f":white_check_mark: I have cleared {amount} messages", delete_after=2
        )

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
    @commands.has_permissions(manage_messages=True)
    async def mute_slash(self, ctx: SlashContext, member, reason=None):
        await self.mute(ctx, member, reason=reason)

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
    @commands.has_permissions(manage_messages=True)
    async def unmute_slash(self, ctx: SlashContext, member):
        await self.unmute(ctx, member=member)

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
    @commands.has_permissions(kick_members=True)
    async def kick_slash(self, ctx: SlashContext, member, reason=None):
        await self.kick(ctx, member, reason=reason)

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
    @commands.has_permissions(ban_members=True)
    async def ban_slash(self, ctx: SlashContext, member, reason=None):
        await self.ban(ctx, member, reason=reason)

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
    @commands.has_permissions(manage_channels=True)
    async def lockdown_slash(
        self, ctx: SlashContext, channel: discord.TextChannel = None
    ):
        await self.lockdown(ctx, channel=channel)

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
    @commands.has_permissions(manage_channels=True)
    async def unlock_slash(
        self, ctx: SlashContext, channel: discord.TextChannel = None
    ):
        await self.unlock(ctx, channel=channel)


# Add cog
def setup(client):
    client.add_cog(Moderation(client))
