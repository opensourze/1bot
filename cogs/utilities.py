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
            weather_embed.set_footer(f"Weather requested by {ctx.author.name}")

            await ctx.send(embed=weather_embed)

    # Avatar command
    @commands.command(
        help="Get your/any user's avatar", brief="Get a user's avatar", aliases=["av"]
    )
    async def avatar(self, ctx, *, user: commands.MemberConverter = None):
        user = user or ctx.author  # Set to author if user is None
        avatar_embed = discord.Embed(color=0xFF6600, title=f"{user.name}'s avatar")
        avatar_embed.set_image(url=f"{user.avatar_url}")
        await ctx.send(embed=avatar_embed)

    # Server Info command
    @commands.command(
        help="View information about the current server",
        brief="View server info",
        aliases=["server"],
    )
    async def serverinfo(self, ctx):
        owner = await self.client.fetch_user(ctx.guild.owner_id)

        embed = discord.Embed(title=f"{ctx.guild.name} information", color=0xFF6600)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Owner", value=f"{owner.name}#{owner.discriminator}")
        embed.add_field(name="Created on", value=str(ctx.guild.created_at)[:10])
        embed.add_field(name="Region", value=str(ctx.guild.region).capitalize())
        embed.add_field(name="Member count", value=ctx.guild.member_count)
        embed.add_field(name="Emojis", value=f"{len(ctx.guild.emojis)} emojis")
        embed.add_field(name="Boost level", value=f"Level {ctx.guild.premium_tier}")

        await ctx.send(embed=embed)

    # User Info command
    @commands.command(help="View a member's information", aliases=["whois"])
    async def userinfo(self, ctx, *, member: commands.MemberConverter = None):
        member = member or ctx.author

        roles = [role for role in member.roles]

        embed = discord.Embed(name=member.name, color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Account creation date", value=str(member.created_at)[:10])
        embed.add_field(name="Joined this server on", value=str(member.joined_at)[:10])
        embed.add_field(
            name=f"Roles ({len(roles)})",
            value=" ".join([role.mention for role in roles]),
            inline=False,
        )
        embed.add_field(name="Is this user a bot?", value=member.bot)

        await ctx.send(embed=embed)

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
    async def weather_slash(self, ctx: SlashContext, city):
        await self.weather(ctx, query=city)

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

    @cog_ext.cog_slash(
        name="serverinfo", description="View information about the current server"
    )
    async def serverinfo_slash(self, ctx: SlashContext):
        await self.serverinfo(ctx)

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


# Add cog
def setup(client):
    client.add_cog(Utilities(client))
