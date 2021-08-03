import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    # Nickname command
    @commands.command(help="Change someone's nickname", aliases=["nick"])
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(
        self, ctx, member: commands.MemberConverter, *, nickname: str = None
    ):
        try:
            await member.edit(nick=nickname)
            await ctx.send(f"`{member}`'s nickname has been changed to `{nickname}`.")
        except discord.Forbidden:
            await ctx.send(
                ":x: I don't have permission to change that user's nickname.\n"
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
    @commands.has_permissions(manage_nicknames=True)
    async def nickname_slash(self, ctx: SlashContext, member, nickname: str = None):
        await self.nickname(ctx, member, nickname=nickname)

    # Role commands
    @commands.group(invoke_without_command=True, help="Create or delete roles")
    @commands.has_permissions(manage_roles=True)
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
    @commands.has_permissions(manage_roles=True)
    async def create(self, ctx, *, name: str):
        await ctx.guild.create_role(name=name)
        await ctx.send(f":white_check_mark: Role `{name}` has been created")

    @role.command(help="Delete a role", aliases=["d"])
    @commands.has_permissions(manage_roles=True)
    async def delete(self, ctx, *, role: commands.RoleConverter):
        await role.delete()
        await ctx.send(f":white_check_mark: Role `{role.name}` has been deleted")

    @role.command(help="Add a role to a member", aliases=["a"])
    @commands.has_permissions(manage_roles=True)
    async def add(
        self, ctx, member: commands.MemberConverter, *, role: commands.RoleConverter
    ):
        await member.add_roles(role)
        await ctx.send(f":white_check_mark: Role `{role}` has been added to {member}.")

    @role.command(help="Remove a role from a member", aliases=["r"])
    @commands.has_permissions(manage_roles=True)
    async def remove(
        self, ctx, member: commands.MemberConverter, *, role: commands.RoleConverter
    ):
        await member.remove_roles(role)
        await ctx.send(
            f":white_check_mark: Role `{role}` has been removed from {member}."
        )

    @cog_ext.cog_subcommand(
        base="role",
        name="create",
        description="Create a new role",
    )
    @commands.has_permissions(manage_roles=True)
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
    @commands.has_permissions(manage_roles=True)
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
    @commands.has_permissions(manage_roles=True)
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
    @commands.has_permissions(manage_roles=True)
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
    @commands.has_permissions(manage_messages=True)
    async def clear_slash(self, ctx: SlashContext, amount: int = 5):
        await self.clear(ctx, amount=amount - 1)
        await ctx.send(
            f":white_check_mark: I have cleared {amount} messages", delete_after=2
        )

    # Slowmode command
    @commands.command(
        help="Set slowmode for the current channel", aliases=["slow", "sm"]
    )
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        if seconds < 0:
            await ctx.send(":x: Slowmode must be a positive number")
            return
        elif seconds > 21600:
            await ctx.send(":x: Slowmode must be less than 21600 seconds (6 hours)")
        else:
            await ctx.channel.edit(slowmode_delay=seconds)

        await ctx.send(f":white_check_mark: Slowmode set to {seconds} seconds")

    @cog_ext.cog_slash(
        name="slowmode", description="Set slowmode for the current channel"
    )
    @commands.has_permissions(manage_channels=True)
    async def slowmode_slash(self, ctx: SlashContext, seconds: int):
        await self.slowmode(ctx, seconds=seconds)

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

        if bot_role <= member.top_role:
            await ctx.send(
                ":x: The user has a higher role or the same top role as mine.\n"
                + "Please move my role higher!"
            )
            return

        if not muted_role:
            await ctx.send(
                ":information_source: Couldn't find a Muted role in this server. Creating a new one..."
            )
            muted_role = await ctx.guild.create_role(name="Muted", color=0xFF0000)

            for channel in ctx.guild.channels:
                await channel.set_permissions(
                    muted_role, send_messages=False, speak=False
                )

        if bot_role <= muted_role:
            await ctx.send(
                ":x: My role is too low. I can only mute users if my role is higher than the Muted role!"
            )
            return

        await member.add_roles(muted_role, reason=reason)

        embed = discord.Embed(
            title="✅ Member muted",
            color=0xFF6600,
            description=f"{member.mention} was muted by {ctx.author.mention}",
            timestamp=ctx.message.created_at,
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
    @commands.has_permissions(manage_messages=True)
    async def mute_slash(self, ctx: SlashContext, member, reason=None):
        await self.mute(ctx, member, reason=reason)

    # Unmute command
    @commands.command(help="Unmute a member")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, *, member: commands.MemberConverter):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(muted_role)

        embed = discord.Embed(
            title="✅ Member muted",
            color=0xFF6600,
            description=f"{member.mention} was muted by {ctx.author.mention}",
            timestamp=ctx.message.created_at,
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
    @commands.has_permissions(manage_messages=True)
    async def unmute_slash(self, ctx: SlashContext, member):
        await self.unmute(ctx, member=member)

    # Kick command
    @commands.command(
        help="Kick a member by mention/ID/username/nickname, optional reason",
        brief="Kick a member",
    )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: commands.MemberConverter, *, reason=None):
        if member == ctx.author:
            await ctx.send(":x: You can't kick yourself!")
            return

        if member.id == self.client.user.id:
            await ctx.send(":x: I can't kick myself!")
            return

        bot = ctx.guild.get_member(self.client.user.id)
        bot_role = bot.top_role

        if bot_role <= member.top_role:
            await ctx.send(
                ":x: The user has a higher role or the same top role as mine.\n"
                + "Please move my role higher!"
            )
            return
        try:
            await member.send(
                f":exclamation: You were kicked from {ctx.guild.name}. Reason: {reason}"
            )
        except:
            pass
        await ctx.guild.kick(member, reason=reason)

        embed = discord.Embed(
            title="✅ Member kicked",
            color=0xFF6600,
            description=f"{member.mention} was kicked by {ctx.author.mention}",
            timestamp=ctx.message.created_at,
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
    @commands.has_permissions(kick_members=True)
    async def kick_slash(self, ctx: SlashContext, member, reason=None):
        await self.kick(ctx, member, reason=reason)

    # Ban command
    @commands.command(
        help="Ban a member by mention/ID/username/nickname, optional reason",
        brief="Ban a member",
    )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: commands.UserConverter, *, reason=None):
        member = ctx.guild.get_member(member.id) or member

        if member == ctx.author:
            await ctx.send(":x: You can't ban yourself!")
            return

        if member.id == self.client.user.id:
            await ctx.send(":x: I can't ban myself!")
            return

        bot = ctx.guild.get_member(self.client.user.id)
        bot_role = bot.top_role

        if isinstance(member, discord.Member) and bot_role <= member.top_role:
            await ctx.send(
                ":x: The user has a higher role or the same top role as mine.\n"
                + "Please move my role higher!"
            )
            return
        try:
            await member.send(
                f":exclamation: You were banned from {ctx.guild.name}! Reason: {reason}"
            )
        except:
            pass
        await ctx.guild.ban(member, reason=reason)

        embed = discord.Embed(
            title="✅ Member banned",
            color=0xFF6600,
            description=f"{member.mention} was banned by {ctx.author.mention}",
            timestamp=ctx.message.created_at,
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
    @commands.has_permissions(ban_members=True)
    async def ban_slash(self, ctx: SlashContext, member, reason=None):
        await self.ban(ctx, member, reason=reason)

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
        await channel.set_permissions(ctx.guild.me, send_messages=True)

        embed = discord.Embed(
            title="✅ Channel locked down",
            color=0xFF6600,
            description=f"{channel.mention} was locked down by {ctx.author.mention}.\n"
            + "Members cannot send messages in the channel now.",
            timestamp=ctx.message.created_at,
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
    @commands.has_permissions(manage_channels=True)
    async def lockdown_slash(
        self, ctx: SlashContext, channel: discord.TextChannel = None
    ):
        await self.lockdown(ctx, channel=channel)

    # Lockdown Unlock command
    @commands.command(
        help="Remove a channel from lockdown", brief="Remove a channel from lockdown"
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=None)

        embed = discord.Embed(
            title="✅ Channel removed from lockdown",
            color=0xFF6600,
            description=f"{channel.mention} was unlocked by {ctx.author.mention}",
            timestamp=ctx.message.created_at,
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
    @commands.has_permissions(manage_channels=True)
    async def unlock_slash(
        self, ctx: SlashContext, channel: discord.TextChannel = None
    ):
        await self.unlock(ctx, channel=channel)


# Add cog
def setup(client):
    client.add_cog(Moderation(client))
