import os
import random
from asyncio import sleep
from io import BytesIO

import discord
import requests
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from PIL import Image


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    # Dad joke command
    @commands.command(help="Get a random dad joke", brief="Get a random dad joke")
    async def dadjoke(self, ctx):
        json = requests.get(
            "https://official-joke-api.appspot.com/jokes/general/random"
        ).json()[0]
        await ctx.send(f"**{json['setup']}**\n\n{json['punchline']}")

    # Programming joke command
    @commands.command(
        help="Get a random programming-related joke",
        brief="Get a programming joke",
        aliases=["codingjoke"],
    )
    async def programmingjoke(self, ctx):
        json = requests.get(
            "https://official-joke-api.appspot.com/jokes/programming/random"
        ).json()[0]
        await ctx.send(f"**{json['setup']}**\n\n{json['punchline']}")

    # Reddit/meme command
    @commands.command(
        help="Get a random meme from Reddit (optionally provide any subreddit)",
        brief="Get a random meme from Reddit",
        aliases=["reddit"],
    )
    @commands.bot_has_permissions(embed_links=True)
    async def meme(self, ctx, subreddit=None):
        if subreddit is not None:
            json = requests.get(
                f"https://meme-api.herokuapp.com/gimme/{subreddit}"
            ).json()
        else:
            json = requests.get(f"https://meme-api.herokuapp.com/gimme").json()

        try:
            if json["code"]:  # If there is an error code...
                await ctx.send(json["message"])  # Send the error message
        except KeyError:
            if json["nsfw"] == False:
                meme_embed = discord.Embed(
                    title=json["title"],
                    color=0xFF6600,
                    url=json["postLink"],
                    description=f"r/{json['subreddit']}",
                )
                meme_embed.set_image(url=json["url"])
                await ctx.send(embed=meme_embed)

        if json["nsfw"]:
            await ctx.send(f":exclamation: Warning: NSFW post!\n\n<{json['postLink']}>")

    # GIF command
    @commands.command(
        help="Search for GIFs (filtered) on Tenor",
        brief="Search for GIFs on Tenor",
        aliases=["tenor"],
    )
    async def gif(self, ctx, *, query):
        json = requests.get(
            f"https://g.tenor.com/v1/search?q={query}&key={os.getenv('TENORKEY')}&contentfilter=medium"
        ).json()

        # Send first result
        await ctx.send(json["results"][0]["url"])

    # 8ball command
    @commands.command(
        help="Ask the magic 8-ball a question", name="8ball", aliases=["eightball"]
    )
    async def eightball(self, ctx, *, question):
        responses = [
            # Affirmative
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes, definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            # Non-committal
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not to tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            # Negative
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]

        random_response = random.choice(responses)

        message = await ctx.send(
            f'Your question was: "{question}"\n\n:8ball: *The magic 8-ball says...*'
        )
        await sleep(2)
        # Edit message and add response after two seconds
        await message.edit(
            content=f'Your question was: "{question}"\n\n:8ball: *The magic 8-ball says...*\n**{random_response}**'
        )

    # Coin flip command
    @commands.command(help="Flip a coin", aliases=["coinflip", "flipcoin"])
    async def flip(self, ctx):
        if random.randint(1, 10) <= 5:
            await ctx.send("I flipped a coin for you, it's **heads**!")
        else:
            await ctx.send("I flipped a coin for you, it's **tails**!")

    # AMOGUS command
    @commands.command(
        help="Amogus, but with a member's profile picture", aliases=["sus"]
    )
    async def amogus(self, ctx, *, member: commands.MemberConverter = None):
        try:
            await ctx.trigger_typing()
        except:
            pass

        member = member or ctx.author
        member_av = member.avatar_url_as(size=256)

        data = BytesIO(await member_av.read())
        av = Image.open(data).resize((187, 187))

        amogus = Image.open("amogus-template.png")

        # Paste the avatar onto the amogus image
        amogus.paste(av, (698, 209))
        amogus.save("amogus.png")

        await ctx.send(
            f"when the {member.name} is sus", file=discord.File("amogus.png")
        )

    # Slash commands
    @cog_ext.cog_slash(name="dadjoke", description="Get a random dad joke")
    async def dadjoke_slash(self, ctx: SlashContext):
        await self.dadjoke(ctx)

    @cog_ext.cog_slash(
        name="programmingjoke", description="Get a programming-related joke"
    )
    async def programmingjoke_slash(self, ctx: SlashContext):
        await self.programmingjoke(ctx)

    @cog_ext.cog_slash(
        name="reddit",
        description="Get a random post from meme subreddits, optionally provide a custom subreddit",
        options=[
            create_option(
                name="subreddit",
                description="Subreddit to get a post from (optional)",
                required=False,
                option_type=3,
            )
        ],
    )
    async def reddit_slash(self, ctx: SlashContext, subreddit: str = None):
        await self.meme(ctx, subreddit=subreddit)

    @cog_ext.cog_slash(name="gif", description="Search for GIFs (filtered) on Tenor")
    async def gif_slash(self, ctx: SlashContext, *, query):
        await self.gif(ctx, query=query)

    @cog_ext.cog_slash(
        name="8ball",
        description="Ask the magic 8-ball a question",
        options=[
            create_option(
                name="question",
                description="What do you want to ask?",
                required=True,
                option_type=3,
            )
        ],
    )
    async def eightball_slash(self, ctx: SlashContext, question):
        await self.eightball(ctx, question=question)

    @cog_ext.cog_slash(name="coinflip", description="Flip a coin")
    async def flip_slash(self, ctx: SlashContext):
        await self.flip(ctx)

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


# Add cog
def setup(client):
    client.add_cog(Fun(client))
