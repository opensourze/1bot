import discord
from discord.ext import commands
import requests


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun cog is ready")

    @commands.command(help="Get a random dad joke", brief="Get a random dad joke")
    async def dadjoke(self, ctx):
        async with ctx.typing():
            r = requests.get(
                "https://official-joke-api.appspot.com/jokes/general/random").json()[0]
        await ctx.send(f"**{r['setup']}**\n\n{r['punchline']}")

    @commands.command(
        help="Get a random programming-related dad joke",
        brief="Get a programming dad joke",
        aliases=["codingjoke", "codingdadjoke", "programmingdadjoke"]
    )
    async def programmingjoke(self, ctx):
        async with ctx.typing():
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
        async with ctx.typing():
            if subreddit is not None:
                r = requests.get(
                    f"https://meme-api.herokuapp.com/gimme/{subreddit}").json()
            else:
                r = requests.get(
                    f"https://meme-api.herokuapp.com/gimme").json()
        try:
            if r["code"]:
                await ctx.send(r["message"])
        except KeyError:
            if r["nsfw"] == False:
                await ctx.send(r["postLink"])

        if r["nsfw"]:
            await ctx.send(f"Warning: NSFW post!\n\n<{r['postLink']}>")


def setup(client):
    client.add_cog(Fun(client))
