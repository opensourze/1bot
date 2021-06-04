import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation cog is ready")

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
        async with ctx.typing():
            await ctx.guild.kick(member, reason=reason)
        await ctx.send(f"Kicked {member.mention}")

    # Ban command
    @commands.command(help="Ban a member by mention/ID/username/nickname, optional reason", brief="Ban a member")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: commands.MemberConverter, *, reason=None):
        async with ctx.typing():
            await ctx.guild.ban(member, reason=reason)
        await ctx.send(f"Banned {member.mention}")

    # Unban command
    @commands.command(help="Unban a member by ID/tag", brief="Unban a member")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        async with ctx.typing():

            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    await ctx.send(f"Unbanned {user.mention}")
                    return

    # Lockdown command
    @commands.command(
        help="Remove permissions for members to send messages in a channel. Optional: provide a channel to lock (defaults to the channel you are inside)",
        brief="Make a channel read-only",
        aliases=["readonly"]
    )
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        async with ctx.typing():
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"I have locked down {channel.mention}.")

    # Lockdown Unlock command
    @commands.command(help="Remove a channel from lockdown", brief="Remove a channel from lockdown")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        async with ctx.typing():
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f"I have unlocked {channel.mention}.")


def setup(client):
    client.add_cog(Moderation(client))
