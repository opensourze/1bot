import platform

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from utils import cluster

banned = cluster["1bot"]["bans"]

__version__ = "0.8.2"


class Miscellaneous(commands.Cog, description="Other miscellaneous commands."):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.emoji = "<:miscellaneous:907550152775073802>"

    # Bot info command
    @commands.command(
        help="View the bot's information",
        brief="View 1Bot's information",
        aliases=["stats", "information", "botinfo"],
    )
    async def info(self, ctx):
        cmd_list = [c for c in self.client.commands if not c.hidden]

        embed = discord.Embed(
            title="1Bot Stats and Information", colour=self.client.colour
        )
        embed.add_field(name="Bot version", value=f"v{__version__}", inline=False)
        embed.add_field(
            name="Command count", value=f"{len(cmd_list)} commands", inline=False
        )
        embed.add_field(
            name="Source code",
            value="View the bot's source code on [GitHub](https://github.com/opensourze/1bot)",
            inline=False,
        )
        embed.add_field(name="Servers", value=f"{len(self.client.guilds)} servers")
        embed.add_field(
            name="Users",
            value=f"{sum([len(guild.members)for guild in self.client.guilds])} users",
        )
        embed.add_field(name="Pycord version", value=discord.__version__, inline=False)
        embed.add_field(
            name="Python version", value=platform.python_version(), inline=False
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed.set_footer(
            text="Copyright (C) 2021 OpenSourze. 1Bot is free and open source under the GNU Affero General Public License version 3.0."
        )
        await ctx.send(embed=embed, components=[self.client.info_btns])

    @cog_ext.cog_slash(name="info", description="View the bot's information")
    async def info_slash(self, ctx: SlashContext):
        await self.info(ctx)

    # Suggest command
    @commands.command(help="Submit a suggestion for the bot")
    @commands.cooldown(1, 900, commands.BucketType.guild)
    async def suggest(self, ctx, *, suggestion):
        result = banned.find_one({"_id": ctx.author.id})

        if result:
            return await ctx.send("❌ You are blocked from submitting suggestions.")

        # Get 1Bot support server's suggestions channel
        channel = self.client.get_channel(884095439190786059)

        embed = discord.Embed(
            title="Suggestion", description=suggestion, colour=self.client.colour
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        message = await channel.send(embed=embed)
        await ctx.send(
            "✅ Your suggestion has been submitted to 1Bot's server! A link to the server can be found in my About Me, or the `info` command.",
        )
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    @cog_ext.cog_slash(name="suggest", description="Submit a suggestion for the bot")
    @commands.cooldown(1, 900, commands.BucketType.guild)
    async def suggest_slash(self, ctx: SlashContext, suggestion):
        await self.suggest(ctx, suggestion=suggestion)

    # Avatar command
    @commands.command(
        help="Get your/any user's avatar",
        brief="Get a user's avatar",
        aliases=["av", "pfp"],
    )
    async def avatar(self, ctx, *, member: commands.MemberConverter = None):
        member = member or ctx.author  # Set to author if user is None

        embed = discord.Embed(
            colour=self.client.colour, title=f"{member.name}'s avatar"
        )
        embed.set_image(url=f"{member.avatar_url}")
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="avatar",
        description="Get a user's avatar",
        options=[
            create_option(
                name="member",
                description="Which user's avatar do you want to see?",
                required=True,
                option_type=6,
            )
        ],
    )
    async def avatar_slash(self, ctx: SlashContext, *, member):
        await self.avatar(ctx, member=member)

    # Server Info command
    @commands.command(
        help="View information about the current server",
        brief="View server info",
        aliases=["server"],
    )
    @commands.guild_only()
    async def serverinfo(self, ctx):
        humans = [mem for mem in ctx.guild.members if not mem.bot]
        bots = [mem for mem in ctx.guild.members if mem.bot]

        embed = discord.Embed(
            title=f"{ctx.guild.name} information", colour=self.client.colour
        )

        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(
            name="Owner",
            value=ctx.guild.owner.mention,
        )
        embed.add_field(
            name="Server created",
            value=f"<t:{round(ctx.guild.created_at.timestamp())}:R>",
        )
        embed.add_field(
            name="Region",
            value=str(ctx.guild.region).capitalize(),
        )
        embed.add_field(
            name="Total member count",
            value=ctx.guild.member_count,
        )
        embed.add_field(
            name="Humans",
            value=f"{len(humans)} human members",
        )
        embed.add_field(
            name="Bots",
            value=f"{len(bots)} bots",
        )
        embed.add_field(
            name="Emojis",
            value=f"{len(ctx.guild.emojis)} emojis",
        )
        embed.add_field(
            name="Roles",
            value=f"{len(ctx.guild.roles)} roles",
        )
        embed.add_field(
            name="Boost level",
            value=f"Level {ctx.guild.premium_tier}",
        )
        embed.add_field(name="Categories", value=f"{len(ctx.guild.categories)}")
        embed.add_field(
            name="Text channels",
            value=len(ctx.guild.text_channels),
        )
        embed.add_field(
            name="Voice channels",
            value=len(ctx.guild.voice_channels),
        )

        embed.set_footer(text=f"Shard {ctx.guild.shard_id} | Server ID {ctx.guild.id}")

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="serverinfo", description="View information about the current server"
    )
    async def serverinfo_slash(self, ctx: SlashContext):
        await self.serverinfo(ctx)

    # Member count command
    @commands.command(
        help="View the number of humans and bots in the server",
        aliases=["members", "mem"],
    )
    @commands.guild_only()
    async def membercount(self, ctx):
        humans = [mem for mem in ctx.guild.members if not mem.bot]
        bots = [mem for mem in ctx.guild.members if mem.bot]

        embed = discord.Embed(
            title=f"{ctx.guild.name} member info", colour=self.client.colour
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(
            name="Humans",
            value=f"**{len(humans)} human members** are in this server",
            inline=False,
        )
        embed.add_field(
            name="Bots", value=f"**{len(bots)} bots** are in this server", inline=False
        )
        embed.add_field(
            name="Total member count",
            value=f"**{ctx.guild.member_count} members in total**",
            inline=False,
        )

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="membercount",
        description="View the number of humans and bots in the server",
    )
    async def membercount_slash(self, ctx: SlashContext):
        await self.membercount(ctx)

    # User Info command
    @commands.command(help="View a member's information", aliases=["whois", "user"])
    @commands.guild_only()
    async def userinfo(self, ctx, *, member: commands.MemberConverter = None):
        member = member or ctx.author

        roles = [role.mention for role in member.roles][::-1][:-1] or ["None"]
        if roles[0] == "None":
            role_length = 0
        else:
            role_length = len(roles)

        embed = discord.Embed(title=member.name, colour=member.colour)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(
            name="Account created",
            value=f"<t:{round(member.created_at.timestamp())}:R>",
        )
        embed.add_field(
            name="Joined this server",
            value=f"<t:{round(member.joined_at.timestamp())}:R>",
        )
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        embed.add_field(name="Join position", value=str(members.index(member) + 1))
        embed.add_field(name="Display name", value=member.display_name)
        if len(" ".join(roles)) <= 1024:
            embed.add_field(
                name=f"Roles ({role_length})",
                value=" ".join(roles),
                inline=False,
            )
        else:
            embed.add_field(
                name=f"Roles ({role_length})",
                value="**[Only showing first 5 roles since there are too many roles to show]**\n"
                + " ".join(roles[:5]),
                inline=False,
            )

        if member.bot:
            embed.add_field(name="Is this user a bot?", value="Yes, beep boop")
        else:
            embed.add_field(name="Is this user a bot?", value="No - normal human user")

        embed.set_footer(text=f"User ID: {member.id}")

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="userinfo",
        description="View information about a user",
        options=[
            create_option(
                name="member",
                description="Which user's information do you want to see?",
                option_type=6,
                required=True,
            )
        ],
    )
    async def userinfo_slash(self, ctx: SlashContext, member):
        await self.userinfo(ctx, member=member)

    # Upvote command
    @commands.command(help="Upvote me on Top.gg", aliases=["vote"])
    async def upvote(self, ctx):
        embed = discord.Embed(
            title="Upvote 1Bot",
            description="Help 1Bot grow by upvoting it on Top.gg!\n\nLink to upvote: **https://top.gg/bot/884080176416309288/vote**",
            colour=self.client.colour,
        )
        embed.set_footer(text="You can upvote every 12 hours. Thank you!")
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="upvote", description="Upvote me on Top.gg")
    async def upvote_slash(self, ctx: SlashContext):
        await self.upvote(ctx)

    # Ping command
    @commands.command(
        help="Tests the bot's latency and displays it in milliseconds",
        brief="Tests the bot's latency",
    )
    async def ping(self, ctx):
        await ctx.send(
            f"Pong! The bot's latency is `{round(self.client.latency * 1000)}ms`"
        )

    @cog_ext.cog_slash(name="ping", description="Test the bot's latency")
    async def ping_slash(self, ctx: SlashContext):
        await self.ping(ctx)

    # Invite command
    @commands.command(help="Add the bot to your server", aliases=["addbot"])
    async def invite(self, ctx):
        await ctx.send(
            "Here's the link to add the bot to your server. Thanks!\nhttps://dsc.gg/1bot"
        )

    @cog_ext.cog_slash(name="invite", description="Add the bot to your server")
    async def invite_slash(self, ctx: SlashContext):
        await ctx.send(
            "Here's the link to add the bot to your server. Thanks!\nhttps://dsc.gg/1bot"
        )

    # Changelog
    @commands.command(help="See what's new in the latest version of 1Bot")
    async def changelog(self, ctx):
        changelog = discord.Embed(
            title=f"What's new in version {__version__} of 1Bot",
            colour=self.client.colour,
            description="Discord Together games disabled TEMPORARILY. A cooldown has been added to the suggest command too, to prevent spam.",
        )

        await ctx.send(embed=changelog)

    @cog_ext.cog_slash(
        name="changelog", description="See what's new in the latest version of 1Bot"
    )
    async def changelog_slash(self, ctx: SlashContext):
        await self.changelog(ctx)


def setup(client):
    client.add_cog(Miscellaneous(client))
