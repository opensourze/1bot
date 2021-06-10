import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
import requests


class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    # Search repositories
    @commands.command(help="Search for GitHub repositories", brief="Search GitHub repositories", aliases=["searchrepo", "githubrepos", "github"])
    async def githubsearch(self, ctx, *, query):
        r = requests.get(
            f"https://api.github.com/search/repositories?q={query}").json()
        if r["total_count"] == 0:
            await ctx.send("No matching repositories found")
        else:
            await ctx.send(f"First result for '{query}':\n{r['items'][0]['html_url']}")

    # Slash commands
    @cog_ext.cog_slash(
        name="search_github",
        description="Search for repositories on GitHub"
    )
    async def githubsearch_slash(self, ctx: SlashContext, *, query):
        await self.githubsearch(ctx, query=query)


def setup(client):
    client.add_cog(Utilities(client))
