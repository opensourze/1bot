import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
import requests
from random import choice


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
        aliases=["codingjoke", "codingdadjoke", "programmingdadjoke"],
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
            await ctx.send(f"Warning: NSFW post!\n\n<{json['postLink']}>")

    # 8ball command
    @commands.command(help="Ask the magic 8-ball a question", aliases=["8ball"])
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

        random_response = choice(responses)
        await ctx.send(
            f'Your question was: "{question}"\n\n*The magic 8-ball says...*\n\n{random_response}'
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

    @cog_ext.cog_slash(
        name="8ball",
        description="Ask the magic 8-ball a question",
        options=[
            create_option(
                name="question",
                description="What do you want to ask?",
                required=True,
                option_type=3
            )
        ]
    )
    async def eightball_slashes(self, ctx: SlashContext, question):
        await self.eightball(ctx, question=question)


# Add cog
def setup(client):
    client.add_cog(Fun(client))
