from contextlib import suppress
from io import BytesIO

import discord
import requests
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from PIL import Image


class Images(commands.Cog, description="Generate fun images!"):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.emoji = "<:images:884089121633611836>"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    neko_url = "https://nekobot.xyz/api/imagegen?type="

    # amogus
    @commands.command(
        help="Amogus, but with a member's profile picture", aliases=["sus", "amongus"]
    )
    async def amogus(self, ctx, *, member: commands.MemberConverter = None):
        try:
            if not ctx.message.attachments:
                member = member or ctx.author
                img = member.avatar_url_as(size=256)
            else:
                img = ctx.message.attachments[0]
        except AttributeError:  # ctx.message is None on slash commands
            member = member or ctx.author
            img = member.avatar_url_as(size=256)

        data = BytesIO(await img.read())
        av = Image.open(data).resize((187, 187))

        amogus = Image.open("amogus-template.png")

        # Paste the avatar/attachment onto the amogus image
        amogus.paste(av, (698, 209))
        amogus.save("amogus.png")

        await ctx.send(file=discord.File("amogus.png"))

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
    async def amogus_slash(self, ctx: SlashContext, member):
        await self.amogus(ctx, member=member)

    # Clyde
    @commands.command(help="Generate an image of Clyde saying something")
    async def clyde(self, ctx, *, text: commands.clean_content):
        if len(text) > 70:
            return await ctx.send("❌ Your text is too long, please use shorter text!")

        with suppress(AttributeError):
            await ctx.trigger_typing()

        json = requests.get(url=f"{self.neko_url}clyde&text={text}").json()

        if json["success"]:
            embed = (
                discord.Embed(color=0x5865F2)
                .set_author(
                    name="Hello. Beep boop.",
                    icon_url="https://images.discordapp.net/avatars/373199180161613824/fd9aabc3a14053d0351980bbea67a4f5.png?size=512",
                )
                .set_image(url=json["message"])
            )

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Error: {json['message']}")

    @cog_ext.cog_slash(
        name="clyde",
        description="Generate an image of Clyde saying something",
        options=[
            create_option(
                name="text",
                description="The text you want to make Clyde say",
                required=True,
                option_type=3,
            )
        ],
    )
    async def clyde_slash(self, ctx: SlashContext, text):
        await ctx.defer()
        await self.clyde(ctx, text=text)

    # Captcha
    @commands.command(help="Please select all squares with.. your profile picture.")
    async def captcha(self, ctx, *, member: commands.MemberConverter = None):
        member = member or ctx.author

        with suppress(AttributeError):
            await ctx.trigger_typing()

        json = requests.get(
            url=f"{self.neko_url}captcha&url={member.avatar_url}&username={member.name}"
        ).json()

        if json["success"]:
            embed = discord.Embed(
                color=0xFF6600, title="Please prove that you're not a robot."
            ).set_image(url=json["message"])

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Error: {json['message']}")

    @cog_ext.cog_slash(
        name="captcha",
        description="Please select all squares with.. your profile picture",
        options=[
            create_option(
                name="member",
                description="Whose avatar do you want to use for the captcha?",
                required=True,
                option_type=6,
            )
        ],
    )
    async def captcha_slash(self, ctx: SlashContext, member):
        await ctx.defer()
        await self.captcha(ctx, member=member)

    # Change my mind
    @commands.command(
        aliases=["cmm"], help="Ask people to change your mind about something"
    )
    async def changemymind(self, ctx, *, text: commands.clean_content):
        if len(text) > 78:
            return await ctx.send("❌ Your text is too long, please use shorter text!")

        with suppress(AttributeError):
            await ctx.trigger_typing()

        json = requests.get(url=f"{self.neko_url}changemymind&text={text}").json()

        if json["success"]:
            embed = (
                discord.Embed(color=0xFF6600)
                .set_author(name=f"Change {ctx.author.name}'s mind")
                .set_image(url=json["message"])
            )

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Error: {json['message']}")

    @cog_ext.cog_slash(
        name="changemymind",
        description="Ask people to change your mind about something",
    )
    async def changemymind_slash(self, ctx: SlashContext, *, text):
        await ctx.defer()
        await self.changemymind(ctx, text=text)

    # Tweet
    @commands.command(help="Generate an image of a tweet", aliases=["twitter"])
    async def tweet(self, ctx, *, text: commands.clean_content):
        if len(text) > 75:
            return await ctx.send("❌ Your text is too long, please use shorter text!")

        with suppress(AttributeError):
            await ctx.trigger_typing()

        json = requests.get(
            url=f"{self.neko_url}tweet&text={text}&username={ctx.author.name}"
        ).json()

        if json["success"]:
            embed = discord.Embed(
                color=0x1DA1F2, title=f"{ctx.author.name}'s tweet"
            ).set_image(url=json["message"])

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Error: {json['message']}")

    @cog_ext.cog_slash(name="tweet", description="Generate an image of a tweet")
    async def tweet_slash(self, ctx: SlashContext, *, text):
        await ctx.defer()
        await self.tweet(ctx, text=text)


def setup(client):
    client.add_cog(Images(client))
