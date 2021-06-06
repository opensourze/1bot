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
        help="Clear multiple messages at once (deletes 5 messages by default)", brief="Clear many messages at once",
        aliases=["purge"]
    )
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount+1)

    # Kick command
    @commands.command(help="Kick a member by mention/ID/username/nickname, optional reason", brief="Kick a member")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: commands.MemberConverter, *, reason=None):
        await ctx.guild.kick(member, reason=reason)
        await ctx.send(f"Kicked {member.mention}")

    # Ban command
    @commands.command(help="Ban a member by mention/ID/username/nickname, optional reason", brief="Ban a member")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: commands.MemberConverter, *, reason=None):
        await ctx.guild.ban(member, reason=reason)
        await ctx.send(f"Banned {member.mention}")

    # Lockdown command
    @commands.command(
        help="Remove permissions for members to send messages in a channel. Optional: provide a channel to lock (defaults to the channel you are inside)",
        brief="Make a channel read-only",
        aliases=["readonly"]
    )
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"I have locked down {channel.mention}.")

    # Lockdown Unlock command
    @commands.command(help="Remove a channel from lockdown", brief="Remove a channel from lockdown")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f"I have unlocked {channel.mention}.")

    # Slash commands

    @cog_ext.cog_slash(
        name="clear",
        description="Clear multiple messages at once",
        options=[
            create_option(
                name="amount",
                description="Number of messages to delete (default = 5)",
                required=False,
                option_type=4
            )
        ]
    )
    @commands.has_permissions(manage_messages=True)
    async def clear_slash(self, ctx: SlashContext, amount: int = 5):
        await self.clear(ctx, amount=amount)
        await ctx.send(f"I have cleared {amount} messages", delete_after=2)

    @cog_ext.cog_slash(
        name="kick",
        description="Kick a member from the server",
        options=[
            create_option(
                name="member",
                description="The user to kick",
                required=True,
                option_type=6
            ),
            create_option(
                name="reason",
                description="Why do you want to kick this user? (Optional)",
                required=False,
                option_type=3
            )
        ]
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
                option_type=6
            ),
            create_option(
                name="reason",
                description="Why do you want to ban this user? (Optional)",
                required=False,
                option_type=3
            )
        ]
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
                option_type=7
            )
        ]
    )
    @commands.has_permissions(manage_channels=True)
    async def lockdown_slash(self, ctx: SlashContext, channel: discord.TextChannel = None):
        await self.lockdown(ctx, channel=channel)

    @cog_ext.cog_slash(
        name="unlock",
        description="Remove a channel from lockdown",
        options=[
            create_option(
                name="channel",
                description="The channel to unlock (optional, defaults to the channel you are in)",
                required=False,
                option_type=7
            )
        ]
    )
    @commands.has_permissions(manage_channels=True)
    async def unlock_slash(self, ctx: SlashContext, channel: discord.TextChannel = None):
        await self.unlock(ctx, channel=channel)


def setup(client):
    client.add_cog(Moderation(client))
