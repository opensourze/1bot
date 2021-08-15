import platform

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_actionrow, create_button

__version__ = "0.4.5"


info_btns = create_actionrow(
    *[
        create_button(
            style=ButtonStyle.URL,
            label="Add bot",
            emoji="➕",
            url="https://dsc.gg/1bot",
        ),
        create_button(
            style=ButtonStyle.URL,
            label="Website",
            emoji="🌐",
            url="https://1bot.netlify.app/",
        ),
        create_button(
            style=ButtonStyle.URL,
            label="Join server",
            url="https://discord.gg/4yA6XkfnwR",
        ),
        create_button(
            style=ButtonStyle.URL,
            label="Upvote me",
            emoji="⬆️",
            url="https://discordbotlist.com/bots/1bot/upvote",
        ),
    ]
)


class Miscellaneous(commands.Cog, description="Miscellaneous commands"):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    # Suggest command
    @commands.command(help="Create a suggestion for the bot")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def suggest(self, ctx, *, suggestion):
        # Get 1Bot support server's suggestions channel
        channel = self.client.get_channel(862697260164055082)

        embed = discord.Embed(
            title="Suggestion", description=suggestion, color=0xFF6600
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        message = await channel.send(embed=embed)
        await ctx.send("✅ Your suggestion has been submitted to " + channel.mention)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    @cog_ext.cog_slash(name="suggest", description="Create a suggestion for the bot")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def suggest_slash(self, ctx: SlashContext, suggestion):
        await self.suggest(ctx, suggestion=suggestion)

    # Bot info command
    @commands.command(
        help="View the bot's information",
        brief="View information",
        aliases=["information", "botinfo"],
    )
    async def info(self, ctx):
        info_embed = discord.Embed(title="`1Bot` information", color=0xFF6600)
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
        info_embed.add_field(name="Bot version", value=f"v{__version__}", inline=False)
        info_embed.add_field(
            name="Discord.py version", value=discord.__version__, inline=False
        )
        info_embed.add_field(
            name="Python version", value=platform.python_version(), inline=False
        )
        info_embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=info_embed, components=[info_btns])

    @cog_ext.cog_slash(name="info", description="View the bot's information")
    async def info_slash(self, ctx: SlashContext):
        await self.info(ctx)

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
        owner = await self.client.fetch_user(ctx.guild.owner_id)

        embed = discord.Embed(title=f"{ctx.guild.name} information", color=0xFF6600)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Owner", value=str(owner))
        embed.add_field(
            name="Created at",
            value=ctx.guild.created_at.strftime(" %I:%M %p UTC, %a %d %B %Y"),
        )
        embed.add_field(name="Region", value=str(ctx.guild.region).capitalize())
        embed.add_field(name="Member count", value=ctx.guild.member_count)
        embed.add_field(name="Emojis", value=f"{len(ctx.guild.emojis)} emojis")
        embed.add_field(name="Boost level", value=f"Level {ctx.guild.premium_tier}")

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
            name="Account creation date",
            value=member.created_at.strftime("%a, %d %B %Y, %I:%M %p UTC"),
        )
        embed.add_field(
            name="Joined this server on",
            value=member.joined_at.strftime("%a, %d %B %Y, %I:%M %p UTC"),
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
        embed.add_field(name="Is this user a bot?", value=member.bot)

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
    @commands.command(help="Upvote me on DiscordBotList")
    async def upvote(self, ctx):
        await ctx.send(
            "If you like this bot, upvote it to help it grow!\n"
            + "You can upvote every 12 hours.\n\n"
            + "https://discordbotlist.com/bots/1bot/upvote/"
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


def setup(client):
    client.add_cog(Miscellaneous(client))
