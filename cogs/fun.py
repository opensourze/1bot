import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
import requests


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun cog is ready")

    @commands.command(help="Get a random dad joke", brief="Get a random dad joke")
    async def dadjoke(self, ctx):
        r = requests.get(
            "https://official-joke-api.appspot.com/jokes/general/random").json()[0]
        await ctx.send(f"**{r['setup']}**\n\n{r['punchline']}")

    @commands.command(
        help="Get a random programming-related joke",
        brief="Get a programming joke",
        aliases=["codingjoke", "codingdadjoke", "programmingdadjoke"]
    )
    async def programmingjoke(self, ctx):
        r = requests.get(
            "https://official-joke-api.appspot.com/jokes/programming/random").json()[0]
        await ctx.send(f"**{r['setup']}**\n\n{r['punchline']}")

    @commands.command(
        help="Get a random meme from Reddit (optionally provide any subreddit)",
        brief="Get a random meme from Reddit",
        aliases=["reddit"]
    )
    @commands.bot_has_permissions(embed_links=True)
    async def meme(self, ctx, subreddit=None):
        if subreddit is not None:
            r = requests.get(
                f"https://meme-api.herokuapp.com/gimme/{subreddit}").json()
        else:
            r = requests.get(f"https://meme-api.herokuapp.com/gimme").json()
        try:
            if r["code"]:
                await ctx.send(r["message"])
        except KeyError:
            if r["nsfw"] == False:
                await ctx.send(r["postLink"])

        if r["nsfw"]:
            await ctx.send(f"Warning: NSFW post!\n\n<{r['postLink']}>")

    # Slash commands

    @cog_ext.cog_slash(name="dadjoke", description="Get a random dad joke")
    async def dadjoke_slash(self, ctx: SlashContext):
        await self.dadjoke(ctx)

    @cog_ext.cog_slash(name="programmingjoke", description="Get a programming-related joke")
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
                option_type=3
            )
        ]
    )
    async def reddit_slash(self, ctx: SlashContext, subreddit: str = None):
        await self.meme(ctx, subreddit=subreddit)


def setup(client):
    client.add_cog(Fun(client))
