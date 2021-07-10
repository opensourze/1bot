import asyncio
import contextlib
import io
import os
import textwrap
from traceback import format_exception

import discord
import requests
from discord.ext import buttons, commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from temperature_converter_py import fahrenheit_to_celsius


class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    # Search repositories
    @commands.command(
        help="Search for GitHub repositories",
        aliases=["searchrepo", "githubsearch"],
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

    # Weather command
    @commands.command(
        help="Get weather info for a city. The city name is required. Optionally add state and country codes separated by commas. Example: `1 weather washington,wa,us`, or `1 weather washington`",
        brief="Get weather info for a city",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def weather(self, ctx, *, query):
        json = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={os.environ['OWM_KEY']}&units=imperial"
        ).json()

        # If code is 404 (not found), send an error message
        if int(json["cod"]) == 404:
            await ctx.send(
                ":x: City not found. Provide only the city name, **or:**\n"
                + "The city name with the state code and country code separated by commas.\n"
                + "E.g.: `washington,wa,us` or just `washington`."
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

    # Avatar command
    @commands.command(
        help="Get your/any user's avatar",
        brief="Get a user's avatar",
        aliases=["av", "pfp"],
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
    @commands.guild_only()
    async def serverinfo(self, ctx):
        owner = await self.client.fetch_user(ctx.guild.owner_id)

        embed = discord.Embed(title=f"{ctx.guild.name} information", color=0xFF6600)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Owner", value=str(owner))
        embed.add_field(name="Created on", value=str(ctx.guild.created_at)[:10])
        embed.add_field(name="Region", value=str(ctx.guild.region).capitalize())
        embed.add_field(name="Member count", value=ctx.guild.member_count)
        embed.add_field(name="Emojis", value=f"{len(ctx.guild.emojis)} emojis")
        embed.add_field(name="Boost level", value=f"Level {ctx.guild.premium_tier}")

        await ctx.send(embed=embed)

    # User Info command
    @commands.command(help="View a member's information", aliases=["whois", "user"])
    @commands.guild_only()
    async def userinfo(self, ctx, *, member: commands.MemberConverter = None):
        member = member or ctx.author

        roles = [role.mention for role in member.roles][::-1][:-1] or ["None"]
        if roles[0] == "None":
            role_length = 0
        else:
            role_length = len(roles)

        embed = discord.Embed(title=member.name, color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Account creation date", value=str(member.created_at)[:10])
        embed.add_field(name="Joined this server on", value=str(member.joined_at)[:10])
        if len(" ".join(roles)) <= 1024:
            embed.add_field(
                name=f"Roles ({role_length})",
                value=" ".join(roles),
                inline=False,
            )
        else:
            embed.add_field(
                name=f"Roles ({role_length})",
                value="**[Only showing first 5 roles, since there are too many roles to show]**\n"
                + " ".join(roles[:5]),
                inline=False,
            )
        embed.add_field(name="Is this user a bot?", value=member.bot)

        await ctx.send(embed=embed)

    # Embed creator
    @commands.command(aliases=["makeembed", "createembed"], help="Create an embed")
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx):
        voted = requests.get(
            f"https://top.gg/api/bots/{self.client.user.id}/check?userId={ctx.author.id}",
            headers={"Authorization": os.environ["TOPGG_TOKEN"]},
        ).json()["voted"]

        if voted == 1 or ctx.author.id == 748791790798372964:
            await ctx.send(
                "Embed creation process started.\n"
                + "Please send the **title you want to use for the embed** within 60 seconds."
            )
        else:
            await ctx.send(
                ":x: You need to vote for the bot to use this command. Your vote resets every 12 hours.\n"
                + "https://top.gg/bot/848936530617434142/vote"
            )
            return

        try:
            title = await self.client.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60,
            )
            await ctx.send(
                f"Title of the embed will be set to '{title.content}'.\n"
                + "Please send the text to use for the **content of the embed** within 60 seconds."
            )
            desc = await self.client.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60,
            )
            await ctx.send(
                "Please send the text to use as a **footer**.\n"
                + "The footer text will be small and light and will be at the bottom of the embed.\n"
                + "**If you don't want a footer, say 'empty'.**"
            )
            footer = await self.client.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60,
            )
            await ctx.send(
                "Do you want me to display you as the author of the embed?\n"
                + "Please answer with **yes** or **no** within 60 seconds.\n"
                + "__Send anything *other than* yes or no to cancel the embed creation.__"
            )
            author = await self.client.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60,
            )

            await ctx.channel.purge(limit=9)

            embed = discord.Embed(
                title=title.content, color=0xFF6600, description=desc.content
            )

            if author.content.lower() == "yes":
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            elif author.content.lower() != "no":
                await ctx.send(":exclamation: Exiting embed creator.")
                return

            if footer.content.lower() != "empty":
                embed.set_footer(text=footer.content)

            await ctx.send(embed=embed)

        except asyncio.TimeoutError:
            await ctx.send(":x: Command has timed out. Exiting embed creator.")

    # Poll command
    @commands.command(help="Create a poll")
    @commands.guild_only()
    async def poll(self, ctx, question, *, options):
        numbers = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟")

        option_list = options.split("/")

        if len(option_list) > 10:
            await ctx.send(":x: You cannot have more than 10 choices!")
            return
        elif len(option_list) < 2:
            await ctx.send(":x: You need to provide multiple options!")
            return

        embed = discord.Embed(
            title=question,
            colour=0xFF6600,
            description="\n\n".join(
                [
                    f"{numbers[i]} {option_list[i]}"  # number emoji + option
                    for i in range(len(option_list))
                ]
            ),
        )
        embed.set_footer(text=f"Poll created by {str(ctx.author.name)}")

        poll_msg = await ctx.send(embed=embed)

        # loop through emojis until the end of the option list is reached
        for emoji in numbers[: len(option_list)]:
            await poll_msg.add_reaction(emoji)  # react with the number emoji

    # Eval command
    @commands.command(name="eval", aliases=["exec"], hidden=True)
    @commands.is_owner()
    async def _eval(self, ctx, *, code):
        if code.startswith("```") and code.endswith("```"):
            code = "\n".join(code.split("\n")[1:])[:-3]

        local_variables = {
            "discord": discord,
            "commands": commands,
            "client": self.client,
            "ctx": ctx,
            "message": ctx.message,
            "asyncio": asyncio,
        }

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}",
                    local_variables,
                )

                obj = await local_variables["func"]()
                result = f"{stdout.getvalue()}\nReturned: {obj}\n"
        except Exception as e:
            result = "".join(format_exception(e, e, e.__traceback__))

        pager = buttons.Paginator(
            timeout=None,
            color=0xFF6600,
            entries=[result[i : i + 2000] for i in range(0, len(result), 2000)],
            length=1,
            prefix="```\n",
            suffix="```",
        )

        await pager.start(ctx)

    # Slash commands

    @cog_ext.cog_slash(
        name="search_github", description="Search for repositories on GitHub"
    )
    async def github_slash(self, ctx: SlashContext, *, query):
        await self.githubsearch(ctx, query=query)

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
    @commands.cooldown(1, 5, commands.BucketType.user)
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

    @cog_ext.cog_slash(name="make_embed", description="Create an embed")
    async def embed_slash(self, ctx: SlashContext):
        await ctx.send(
            ":x: Unfortunately, this command isn't compatible with slash commands.\n"
            + "**Please use `1embed` or `1 embed` instead."
        )

    @cog_ext.cog_slash(
        name="poll",
        description="Create a poll",
        options=[
            create_option(
                name="question",
                description="The title of the poll",
                required=True,
                option_type=3,
            ),
            create_option(
                name="options",
                description="The choices you want for the poll separated by slashes",
                required=True,
                option_type=3,
            ),
        ],
    )
    async def poll_slash(self, ctx, question, options):
        await self.poll(ctx, question, options=options)


# Add cog
def setup(client):
    client.add_cog(Utilities(client))
