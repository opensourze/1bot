import platform

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_actionrow, create_button

__version__ = "0.6.5"


class Miscellaneous(commands.Cog, description="Other miscellaneous commands."):
    def __init__(self, client):
        self.client = client
        self.emoji = "<:miscellaneous:884088957057523733>"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

        self.info_btns = create_actionrow(
            *[
                create_button(
                    style=ButtonStyle.URL,
                    label="Add me",
                    emoji=self.client.get_emoji(885088268314611732),
                    url="https://dsc.gg/1bot",
                ),
                create_button(
                    style=ButtonStyle.URL,
                    label="Website",
                    emoji=self.client.get_emoji(885099687252750337),
                    url="https://1bot.netlify.app/",
                ),
                create_button(
                    style=ButtonStyle.URL,
                    emoji=self.client.get_emoji(885083336240926730),
                    label="Support Server",
                    url="https://discord.gg/JGcnKxEPsW",
                ),
                create_button(
                    style=ButtonStyle.URL,
                    label="Upvote me",
                    emoji=self.client.get_emoji(885466072373948416),
                    url="https://discordbotlist.com/bots/1bot/upvote",
                ),
            ]
        )

    # Bot info command
    @commands.command(
        help="View the bot's information",
        brief="View 1Bot's information",
        aliases=["information", "botinfo"],
    )
    async def info(self, ctx):
        cmd_list = [c for c in self.client.commands if not c.hidden]

        info_embed = discord.Embed(title="`1Bot` information", color=0xFF6600)
        info_embed.add_field(name="Bot version", value=f"v{__version__}", inline=False)
        info_embed.add_field(
            name="Command count", value=f"{len(cmd_list)} commands", inline=False
        )
        info_embed.add_field(
            name="Source code",
            value="View the bot's source code on [GitHub](https://github.com/opensourze/1bot)",
            inline=False,
        )
        info_embed.add_field(
            name="Developer",
            value="[OpenSourze](https://twitter.com/opensourze)",
            inline=False,
        )
        info_embed.add_field(name="Servers", value=f"{len(self.client.guilds)} servers")
        info_embed.add_field(
            name="Pycord version", value=discord.__version__, inline=False
        )
        info_embed.add_field(
            name="Python version", value=platform.python_version(), inline=False
        )
        info_embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=info_embed, components=[self.info_btns])

    @cog_ext.cog_slash(name="info", description="View the bot's information")
    async def info_slash(self, ctx: SlashContext):
        await self.info(ctx)

    # Suggest command
    @commands.command(help="Submit a suggestion for the bot")
    async def suggest(self, ctx, *, suggestion):
        # Get 1Bot support server's suggestions channel
        channel = self.client.get_channel(884095439190786059)

        embed = discord.Embed(
            title="Suggestion", description=suggestion, color=0xFF6600
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        message = await channel.send(embed=embed)
        await ctx.send("✅ Your suggestion has been submitted to " + channel.mention)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    @cog_ext.cog_slash(name="suggest", description="Submit a suggestion for the bot")
    async def suggest_slash(self, ctx: SlashContext, suggestion):
        await self.suggest(ctx, suggestion=suggestion)

    # Avatar command
    @commands.command(
        help="Get your/any user's avatar",
        brief="Get a user's avatar",
        aliases=["av", "pfp"],
    )
    async def avatar(self, ctx, *, user: commands.MemberConverter = None):
        user = user or ctx.author  # Set to author if user is None
        avatar_embed = discord.Embed(color=0xFF6600, title=f"{user.name}'s avatar")
        avatar_embed.set_image(url=f"{user.avatar_url}")
        await ctx.send(embed=avatar_embed)

    @cog_ext.cog_slash(
        name="avatar",
        description="Get a user's avatar",
        options=[
            create_option(
                name="user",
                description="Which user's avatar do you want to see?",
                required=True,
                option_type=6,
            )
        ],
    )
    async def avatar_slash(self, ctx: SlashContext, *, user):
        await self.avatar(ctx, user=user)

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

        embed = discord.Embed(title=f"{ctx.guild.name} information", color=0xFF6600)

        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Owner", value=ctx.guild.owner.mention, inline=False)
        embed.add_field(
            name="Server created",
            value=f"<t:{round(ctx.guild.created_at.timestamp())}:R>",
            inline=False,
        )
        embed.add_field(
            name="Region", value=str(ctx.guild.region).capitalize(), inline=False
        )
        embed.add_field(
            name="Total member count", value=ctx.guild.member_count, inline=False
        )
        embed.add_field(
            name="Humans", value=f"{len(humans)} human members", inline=False
        )
        embed.add_field(name="Bots", value=f"{len(bots)} bots", inline=False)
        embed.add_field(
            name="Emojis", value=f"{len(ctx.guild.emojis)} emojis", inline=False
        )
        embed.add_field(
            name="Boost level", value=f"Level {ctx.guild.premium_tier}", inline=False
        )

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="serverinfo", description="View information about the current server"
    )
    async def serverinfo_slash(self, ctx: SlashContext):
        await self.serverinfo(ctx)

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

        embed = discord.Embed(title=member.name, color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(
            name="Account created",
            value=f"<t:{round(member.created_at.timestamp())}:R>",
        )
        embed.add_field(
            name="Joined this server",
            value=f"<t:{round(member.joined_at.timestamp())}:R>",
        )
        embed.add_field(name="Nickname", value=member.display_name)
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

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="userinfo",
        description="View information about a user",
        options=[
            create_option(
                name="user",
                description="Which user's information do you want to see?",
                option_type=6,
                required=True,
            )
        ],
    )
    async def userinfo_slash(self, ctx: SlashContext, member):
        await self.userinfo(ctx, member=member)

    # Upvote command
    @commands.command(help="Upvote me on DiscordBotList", aliases=["vote"])
    async def upvote(self, ctx):
        await ctx.send(
            "If you like this bot, upvote it to help it grow!\n"
            + "You can upvote every 12 hours.\n\n"
            + "https://discordbotlist.com/bots/1bot/upvote/\n\n"
            + "Thank you!"
        )

    @cog_ext.cog_slash(name="upvote", description="Upvote me on DiscordBotList")
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
            color=0xFF6600,
            description="New `chess` command that lets you play chess (yes, actual chess) with a friend inside a voice channel. Try it!",
        )

        await ctx.send(embed=changelog)

    @cog_ext.cog_slash(
        name="changelog", description="See what's new in the latest version of 1Bot"
    )
    async def changelog_slash(self, ctx: SlashContext):
        await self.changelog(ctx)


def setup(client):
    client.add_cog(Miscellaneous(client))
