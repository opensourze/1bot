import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
import requests
import os


class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    # Search repositories
    @commands.command(help="Search for GitHub repositories", brief="Search GitHub repositories", aliases=["searchrepo", "githubrepos", "githubsearch"])
    async def github(self, ctx, *, query):
        json = requests.get(
            f"https://api.github.com/search/repositories?q={query}").json()
        if json["total_count"] == 0:
            await ctx.send("No matching repositories found")
        else:
            await ctx.send(f"First result for '{query}':\n{json['items'][0]['html_url']}")

    # GIF command
    @commands.command(help="Search for GIFs (filtered) on Tenor", brief="Search for GIFs on Tenor", aliases=["tenor"])
    async def gif(self, ctx, *, query):

        json = requests.get(
            f"https://g.tenor.com/v1/search?q={query}&key={os.getenv('TENORKEY')}&contentfilter=medium").json()

        if json.code == 200:
            await ctx.send(json['results'][0]['url'])
        else:
            ctx.send(f"Something went wrong - error code {json.code}")

    # Slash commands
    @cog_ext.cog_slash(
        name="search_github",
        description="Search for repositories on GitHub"
    )
    async def github_slash(self, ctx: SlashContext, *, query):
        await self.githubsearch(ctx, query=query)

    @cog_ext.cog_slash(
        name="gif",
        description="Search for GIFs (filtered) on Tenor"
    )
    async def gif_slash(self, ctx: SlashContext, *, query):
        await self.gif(ctx, query=query)


def setup(client):
    client.add_cog(Utilities(client))
