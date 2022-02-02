from contextlib import suppress
from io import BytesIO
from urllib.parse import quote

import discord
import requests
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from PIL import Image


class Images(commands.Cog, description="Generate fun images!"):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.emoji = "<:images:907549693364543538>"

    # amogus
    @commands.command(
        help="Amogus, but with a member's profile picture", aliases=["sus", "amongus"]
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def amogus(self, ctx, *, member: commands.MemberConverter = None):
        try:
            if not ctx.message.attachments:
                member = member or ctx.author
                img = member.avatar_url_as(size=256)
            else:
                img = ctx.message.attachments[0]
        except AttributeError:
            member = member or ctx.author
            img = member.avatar_url_as(size=256)

        data = BytesIO(await img.read())
        av = Image.open(data).resize((187, 187))

        amogus = Image.open("amogus-template.png")

        # Paste the avatar/attachment onto the amogus image
        amogus.paste(av, (698, 209))
        amogus.save("image-outputs/amogus.png")

        await ctx.send(file=discord.File("image-outputs/amogus.png"))

    @cog_ext.cog_slash(
        name="amogus",
        description="Amogus, but with a member's profile picture",
        options=[
            create_option(
                name="member",
                description="The member whose profile picture you want to use",
                required=True,
                option_type=6,
            )
        ],
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def amogus_slash(self, ctx: SlashContext, member):
        await self.amogus(ctx, member=member)

    # Tweet
    @commands.command(help="Generate an image of you tweeting something")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tweet(self, ctx, *, text: str):
        if len(text) >= 1000:
            return await ctx.send(
                "❌ Your text is too long, please use text shorter than 1000 characters!"
            )

        avatar = ctx.author.avatar_url_as(format="png")

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Tweet", colour=0x1DA1F2
        )
        embed.set_image(
            url=f"https://some-random-api.ml/canvas/tweet?comment={quote(text)}&avatar={avatar}&username={quote(ctx.author.name)}&displayname={quote(ctx.author.display_name)}"
        )

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="tweet", description="Generate an image of you tweeting something"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tweet_slash(self, ctx: SlashContext, *, text):
        await self.tweet(ctx, text=text)

    # YouTube comment
    @commands.command(
        help="Generate an image of a YouTube comment by you",
        aliases=["ytcomment", "comment"],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def youtubecomment(self, ctx, *, comment: str):
        if len(comment) >= 1000:
            return await ctx.send(
                "❌ Your text is too long, please use text shorter than 1000 characters!"
            )

        avatar = ctx.author.avatar_url_as(format="png")

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s YouTube comment", colour=0xC4302B
        )
        embed.set_image(
            url=f"https://some-random-api.ml/canvas/youtube-comment?comment={quote(comment)}&username={quote(ctx.author.display_name)}&avatar={avatar}"
        )

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="youtubecomment",
        description="Generate an image of a YouTube comment by you",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ytcomment_slash(self, ctx: SlashContext, *, comment: str):
        await self.youtubecomment(ctx, comment=comment)

    # Wasted
    @commands.command(
        help="Add a Wasted overlay to an avatar or an attached image",
        brief="Add a Wasted overlay to an avatar or image",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def wasted(
        self, ctx: SlashContext, *, member: commands.MemberConverter = None
    ):
        try:
            if not ctx.message.attachments:
                member = member or ctx.author
                img = member.avatar_url_as(format="png")
            else:
                img = ctx.message.attachments[0].url
        except AttributeError:
            member = member or ctx.author
            img = member.avatar_url_as(format="png")

        embed = discord.Embed(title="wasted.", colour=self.client.colour)
        embed.set_image(url=f"https://some-random-api.ml/canvas/wasted?avatar={img}")

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="wasted",
        description="Add a Wasted overlay to someone's avatar",
        options=[
            create_option(
                name="member",
                description="The member whose avatar to add the overlay on",
                required=False,
                option_type=6,
            )
        ],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def wasted_slash(self, ctx: SlashContext, member=None):
        await self.wasted(ctx, member=member)

    # Mission Passed
    @commands.command(
        help="Add a Mission Passed overlay to an avatar or an attached image",
        brief="Add a Mission Passed overlay to avatars or images",
        aliases=["passed"],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def missionpassed(
        self, ctx: SlashContext, *, member: commands.MemberConverter = None
    ):
        try:
            if not ctx.message.attachments:
                member = member or ctx.author
                img = member.avatar_url_as(format="png")
            else:
                img = ctx.message.attachments[0].url
        except AttributeError:
            member = member or ctx.author
            img = member.avatar_url_as(format="png")

        embed = discord.Embed(title="mission passed.", colour=self.client.colour)
        embed.set_image(url=f"https://some-random-api.ml/canvas/passed?avatar={img}")

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="missionpassed",
        description="Add a Mission Passed overlay to someone's avatar",
        options=[
            create_option(
                name="member",
                description="The member whose avatar to add the overlay on",
                required=False,
                option_type=6,
            )
        ],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def missionpassed_slash(self, ctx: SlashContext, member=None):
        await self.missionpassed(ctx, member=member)

    # Triggered
    @commands.command(help="Create a triggered gif with someone's avatar")
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def triggered(self, ctx, *, member: commands.MemberConverter = None):
        with suppress(AttributeError):
            await ctx.trigger_typing()

        member = member or ctx.author
        avatar = member.avatar_url_as(format="png")
        url = f"https://some-random-api.ml/canvas/triggered?avatar={avatar}"

        r = requests.get(url)
        image = Image.open(BytesIO(r.content))
        image.save("image-outputs/triggered.gif", save_all=True)

        file = discord.File("image-outputs/triggered.gif")

        await ctx.send(file=file)

    @cog_ext.cog_slash(
        name="triggered",
        description="Create a triggered gif with someone's avatar",
        options=[
            create_option(
                name="member",
                description="The member whose avatar to add the triggered overlay to",
                required=False,
                option_type=6,
            )
        ],
    )
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def triggered_slash(self, ctx: SlashContext, member=None):
        await ctx.defer()
        await self.triggered(ctx, member=member)

    # Blurple
    @commands.command(
        help="Filter an avatar/image with Discord's blurple colour",
        aliases=["blurplify"],
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def blurple(self, ctx, *, member: commands.MemberConverter = None):
        embed = discord.Embed(title="Your blurple filtered image", colour=0x5865F2)

        try:
            if not ctx.message.attachments:
                member = member or ctx.author
                img = member.avatar_url_as(format="png")
            else:
                img = ctx.message.attachments[0].url
        except AttributeError:
            member = member or ctx.author
            img = member.avatar_url_as(format="png")

        embed.set_image(url=f"https://some-random-api.ml/canvas/blurple2?avatar={img}")

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="blurple",
        description="Filter an avatar with Discord's blurple colour",
        options=[
            create_option(
                name="member",
                description="The member whose avatar to filter",
                required=False,
                option_type=6,
            )
        ],
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def blurple_slash(self, ctx: SlashContext, member=None):
        await self.blurple(ctx, member=member)

    # Woosh / joke over head
    @commands.command(
        help="Create an image of a joke going over someone's head",
        aliases=["whoosh", "jokeoverhead"],
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def woosh(self, ctx, *, member: commands.MemberConverter = None):
        member = member or ctx.author
        avatar = str(member.avatar_url_as(format="png"))[:-10]

        embed = discord.Embed(
            description="Woosh...\nthat's the sound of a joke going over your head.",
            colour=self.client.colour,
        )
        embed.set_image(url=f"https://api.popcat.xyz/jokeoverhead?image={avatar}")

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="woosh",
        description="Create an image of a joke going over someone's head",
        options=[
            create_option(
                name="member",
                description="The member to woosh",
                required=False,
                option_type=6,
            )
        ],
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def woosh_slash(self, ctx: SlashContext, member=None):
        await self.woosh(ctx, member=member)

    # Oogway quote
    @commands.command(
        help="Create an image of a quote from Oogway",
        aliases=["oogway"],
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def oogwayquote(self, ctx, *, text: str):
        embed = discord.Embed(
            title="A quote by Master Oogway", colour=self.client.colour
        )
        embed.set_image(url=f"https://api.popcat.xyz/oogway?text={quote(text)}")

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="oogwayquote",
        description="Create an image of a quote from Oogway",
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def oogwayquote_slash(self, ctx: SlashContext, *, text: str):
        await self.oogwayquote(ctx, text=text)

    # Greyscale
    @commands.command(
        help="Filter an avatar with black and white",
        aliases=["blackandwhite", "grayscale"],
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def greyscale(self, ctx, *, member: commands.MemberConverter = None):
        member = member or ctx.author
        avatar = str(member.avatar_url_as(format="png"))[:-10]

        embed = discord.Embed(
            description=" ",
            colour=self.client.colour,
        )
        embed.set_image(url=f"https://api.popcat.xyz/greyscale?image={avatar}")

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="greyscale",
        description="Filter someone's avatar black and white",
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def greyscale_slash(
        self, ctx: SlashContext, *, member: discord.Member = None
    ):
        await self.greyscale(ctx, member=member)


def setup(client):
    client.add_cog(Images(client))
