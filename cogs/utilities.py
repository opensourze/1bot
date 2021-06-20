import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
import requests
from temperature_converter_py import fahrenheit_to_celsius
import os


class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    # Search repositories
    @commands.command(
        help="Search for GitHub repositories",
        aliases=["searchrepo", "githubrepos", "githubsearch"],
    )
    async def github(self, ctx, *, query):
        json = requests.get(
            f"https://api.github.com/search/repositories?q={query}"
        ).json()

        if json["total_count"] == 0:
            await ctx.send("No matching repositories found")
        else:
            await ctx.send(
                f"First result for '{query}':\n{json['items'][0]['html_url']}"
            )

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

    # Weather command
    @commands.command(
        help="Get weather info for a city. E.g.: _weather imperial Washington,WA,US (unit system: imperial for fahrenheit, metric for celsius), state and country codes optional",
        brief="Get weather info for a city",
    )
    async def weather(self, ctx, *, query):
        json = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={os.getenv('OWM_KEY')}&units=imperial"
        ).json()

        # If code is 404 (not found), send an error message
        if json["cod"] == 404:
            await ctx.send(
                "City not found. Provide only the city name, **or** the city name with the state code and country code separated by commas. E.g.: washington,wa,us"
            )
        else:
            weather_description = json["weather"][0]["description"].capitalize()
            icon_url = (  # icons URL + icon code + @2x.png (for higher resolution icon)
                "https://openweathermap.org/img/wn/"
                + json["weather"][0]["icon"]
                + "@2x.png"
            )
            celsius_temp = fahrenheit_to_celsius(json["main"]["temp"])

            weather_embed = discord.Embed(
                title=f"Weather in {json['name']}",  # "Weather in <city name>"
                description=weather_description,
                color=0xFF6600,
            )
            weather_embed.set_thumbnail(url=icon_url)

            weather_embed.add_field(
                name="Temperature",
                # "<temp. in fahrenheit>° F / <temp. in celsius>° C"
                value=f"{json['main']['temp']}° F / {round(celsius_temp, 2)}° C",
            )
            weather_embed.add_field(
                name="Cloudiness", value=f"{json['clouds']['all']}%"
            )
            weather_embed.add_field(
                name="Humidity", value=f"{json['main']['humidity']}%"
            )
            weather_embed.add_field(
                name="Wind speed", value=f"{json['wind']['speed']} m/s"
            )
            weather_embed.add_field(
                name="Wind direction", value=f"{json['wind']['deg']}°"
            )

            await ctx.send(embed=weather_embed)

    # Slash commands

    @cog_ext.cog_slash(
        name="search_github", description="Search for repositories on GitHub"
    )
    async def github_slash(self, ctx: SlashContext, *, query):
        await self.githubsearch(ctx, query=query)

    @cog_ext.cog_slash(name="gif", description="Search for GIFs (filtered) on Tenor")
    async def gif_slash(self, ctx: SlashContext, *, query):
        await self.gif(ctx, query=query)

    @cog_ext.cog_slash(
        name="weather",
        description="Get weather info for a city",
        options=[
            create_option(
                name="city",
                description="City name. Optionally add state code and country code separated by commas",
                required=True,
                option_type=3,
            )
        ],
    )
    async def weather_slash(self, ctx: SlashContext, *, query):
        await self.weather(ctx, query=query)


# Add cog
def setup(client):
    client.add_cog(Utilities(client))
