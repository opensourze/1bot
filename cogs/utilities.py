import asyncio
import base64
import contextlib
import os

import discord
import requests
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from temperature_converter_py import fahrenheit_to_celsius


class Utilities(
    commands.Cog,
    description="1Bot has some neat utilities to help you out with anything",
):
    def __init__(self, client):
        self.client = client
        self.emoji = "<:utilities:884088853609193544>"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    # Emoji command
    @commands.command(aliases=["createemoji", "addemoji", "emote"])
    @commands.has_permissions(manage_emojis=True)
    @commands.bot_has_permissions(manage_emojis=True)
    async def emoji(self, ctx, *, emoji_name: str):
        if not ctx.message.attachments:
            await ctx.send(f"❌ You need to attach an image to create an emoji!")
            return

        try:
            emoji = await ctx.guild.create_custom_emoji(
                name=emoji_name, image=await ctx.message.attachments[0].read()
            )

        # errors
        except discord.HTTPException as e:
            if "File cannot be larger than 256" in str(e):
                await ctx.send(
                    "❌ The image is too big; please attach an image that is smaller than 256 kb."
                )
                return
            elif "String value did not match validation regex" in str(e):
                await ctx.send(
                    "❌ Invalid emoji name, you might have some unsupported special characters or spaces in the name!"
                )
                return
            elif "Must be between 2 and 32 in length" in str(e):
                await ctx.send("❌ The emoji name must be 2 to 32 characters long.")
                return

        await ctx.send(f"Emoji created! {emoji}")

    # Raw text command
    @commands.command(
        aliases=["rawtext"],
        help="Get the raw, unformatted text of the message you replied to. You can also use a message ID.",
        brief="Get raw text of the message you replied to.",
    )
    async def raw(self, ctx, message_id: int = None):
        message = None  # gets reassigned after message is fetched

        try:
            # try fetching the replied message
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        except (discord.NotFound, AttributeError):  # if the message is not a reply
            if not message_id:
                await ctx.send(
                    "❌ You need to either reply to a message with this command or provide a message ID!"
                )
                return
            else:
                try:
                    message = await ctx.channel.fetch_message(message_id)
                except discord.NotFound:
                    await ctx.send(
                        "❌ The message you provided was not found in this channel!"
                    )

        if not message.content:
            await ctx.send("❌ This message has no content.")
            return

        await ctx.send(f"```{message.content}```")

    @cog_ext.cog_slash(
        name="raw",
        description="Get raw text of a message with its ID",
        options=[
            create_option(
                name="message_id",
                description="The ID of the message to get raw text from",
                required=True,
                option_type=4,
            )
        ],
    )
    async def raw_slash(self, ctx: SlashContext, message_id):
        await self.raw(ctx, message_id=message_id)

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

    @cog_ext.cog_slash(
        name="search_github", description="Search for repositories on GitHub"
    )
    async def github_slash(self, ctx: SlashContext, *, query):
        await self.githubsearch(ctx, query=query)

    # PyPI command
    @commands.command(help="Get info for a PyPI module")
    async def pypi(self, ctx, *, package):
        request = requests.get(f"https://pypi.org/pypi/{package}/json")
        if request.status_code == 404:
            await ctx.send("❌ That module doesn't exist!")
            return

        json = request.json()

        embed = discord.Embed(
            title=json["info"]["name"],
            color=0xFF6600,
            url=json["info"]["package_url"],
        )

        if json["info"]["summary"] != "UNKNOWN":
            embed.description = json["info"]["summary"]

        if len(json["info"]["description"]) <= 1024:
            embed.add_field(
                name="Description", value=json["info"]["description"], inline=False
            )
        else:
            # Slice description to 1021 characters and add ellipsis
            embed.add_field(
                name="Description",
                value=json["info"]["description"][:1021] + "...",
                inline=False,
            )

        if json["info"]["home_page"]:
            embed.add_field(name="Homepage", value=json["info"]["home_page"])

        embed.add_field(name="Version", value=json["info"]["version"])
        embed.add_field(name="Author", value=json["info"]["author"])
        embed.add_field(name="License", value=json["info"]["license"])

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="pypi", description="Get info for a PyPI module")
    async def pypi_slash(self, ctx: SlashContext, *, package):
        await self.pypi(ctx, package=package)

    # NPM command
    @commands.command(help="Get info for an NPM module")
    async def npm(self, ctx, *, package):
        json = requests.get(f"https://registry.npmjs.org/{package}").json()

        try:
            if json["error"]:
                await ctx.send("❌ " + json["error"])
        except KeyError:
            embed = discord.Embed(
                title=json["name"],
                description=json["description"],
                color=0xD50000,
                url="https://www.npmjs.com/package/" + package,
            )

            with contextlib.suppress(KeyError):
                embed.add_field(name="Homepage", value=json["homepage"], inline=False)

            embed.add_field(name="Author", value=json["author"]["name"])

            with contextlib.suppress(KeyError):
                embed.add_field(
                    name="GitHub repository",
                    value=json["repository"]["url"][4:-4],
                    inline=False,
                )
            embed.add_field(
                name="Repository maintainers",
                value=", ".join(
                    maintainer["name"] for maintainer in json["maintainers"]
                ),
                inline=False,
            )
            with contextlib.suppress(KeyError):
                embed.add_field(name="License", value=json["license"], inline=False)

            await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="npm", description="Get info for an NPM module")
    async def npm_slash(self, ctx: SlashContext, *, package):
        await self.npm(ctx, package=package)

    # Lyrics command
    @commands.command(help="Get lyrics for a song", aliases=["ly"])
    async def lyrics(self, ctx, *, song):
        with contextlib.suppress(KeyError):
            await ctx.trigger_typing()

        json = requests.get(f"https://some-random-api.ml/lyrics?title={song}").json()

        with contextlib.suppress(KeyError):
            if json["error"]:
                await ctx.send("❌ " + json["error"])
                return

        embed = discord.Embed(title=json["title"], color=0xFF6600)
        embed.set_author(
            name="Click to view lyrics in your browser", url=json["links"]["genius"]
        )
        embed.set_thumbnail(url=json["thumbnail"]["genius"])

        if len(json["lyrics"]) > 4096:
            embed.description = json["lyrics"][:4093] + "..."
        else:
            embed.description = json["lyrics"]

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="lyrics", description="Get lyrics for a song")
    async def lyrics_slash(self, ctx: SlashContext, *, song):
        await self.lyrics(ctx, song=song)

    # Base64
    @commands.group(
        invoke_without_command=True, help="Encode/decode base64", aliases=["b64"]
    )
    async def base64(self, ctx):
        embed = discord.Embed(
            title="Base64 commands",
            description="Run `1 base64 e {text}` to convert the text into base64.\n"
            + "Run `1 base64 d {base64}` to decode base64 code.\n",
            color=0xFF6600,
        ).set_footer(text="Don't include the brackets while running commands!")

        await ctx.send(embed=embed)

    @base64.command(help="Encode text into base64", aliases=["e"])
    async def encode(self, ctx, *, text):
        await ctx.send(base64.b64encode(text.encode()).decode())

    @base64.command(help="Decode base64 into text", aliases=["d"])
    async def decode(self, ctx, *, code):
        await ctx.send(base64.b64decode(code.encode()).decode())

    @cog_ext.cog_subcommand(
        base="base64", name="encode", description="Encode text into base64"
    )
    async def encode_slash(self, ctx: SlashContext, *, text):
        await self.encode(ctx, text=text)

    @cog_ext.cog_subcommand(
        base="base64", name="decode", description="Decode base64 into text"
    )
    async def decode_slash(self, ctx: SlashContext, *, code):
        await self.decode(ctx, code=code)

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
                "❌ City not found. Provide only the city name, **or:**\n"
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

    # Embed command
    @commands.command(aliases=["makeembed", "createembed"], help="Create an embed")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def embed(self, ctx):
        msg1 = await ctx.send(
            "I'll now ask you to send some messages to use for the embed!\n___"
        )

        msg2 = await ctx.channel.send(
            "Now send the **title you want to use for the embed** within 60 seconds."
        )

        try:
            title_msg = await self.client.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60,
            )
            title = title_msg.content

            if len(title) > 256:
                await ctx.send(
                    "❌ Title is too long. Run the command again but use a shorter title!"
                )
                return

            await msg2.delete()
            await title_msg.delete()

            msg3 = await ctx.channel.send(
                f"Title of the embed will be set to '{title}'.\n"
                + "Now send the text to use for the **content of the embed** within 60 seconds."
            )
            desc_msg = await self.client.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60,
            )

            description = desc_msg.content
            await msg3.delete()
            await desc_msg.delete()

            msg4 = await ctx.channel.send(
                "Please send the text to use as a **footer**.\n"
                + "The footer text will be small and light and will be at the bottom of the embed.\n\n"
                + "**If you don't want a footer, say 'empty'.**"
            )
            footer_msg = await self.client.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60,
            )

            footer = footer_msg.content
            await msg4.delete()
            await footer_msg.delete()

            msg5 = await ctx.channel.send(
                "Do you want me to display you as the author of the embed?\n"
                + "Please answer with **yes** or **no** within 60 seconds.\n\n"
                + "__Send anything *other than* yes or no to cancel__ - the embed will not be sent if you cancel."
            )
            author_msg = await self.client.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60,
            )

            author = author_msg.content
            await msg5.delete()
            await author_msg.delete()

            embed = discord.Embed(title=title, description=description)

            if author.lower() == "yes":
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            elif author.lower() != "no":
                await ctx.send(
                    "❗ Cancelled - you will have to run the command again if you want to make an embed."
                )
                return

            if footer.lower() != "empty":
                embed.set_footer(text=footer)

            await msg1.delete()
            with contextlib.suppress(AttributeError):
                await ctx.message.delete()

            await ctx.channel.send(embed=embed)

        except asyncio.TimeoutError:
            await ctx.channel.send("❌ Command has timed out. Exiting embed creator.")

    @cog_ext.cog_slash(name="embed", description="Create an embed")
    @commands.has_permissions(manage_messages=True)
    async def embed_slash(self, ctx: SlashContext):
        await ctx.defer()
        await self.embed(ctx)

    # Poll command
    @commands.command(help="Create a poll")
    @commands.guild_only()
    async def poll(self, ctx, question, *, options):
        numbers = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟")

        option_list = options.split("/")

        if len(option_list) > 10:
            await ctx.send("❌ You cannot have more than 10 choices!")
            return
        elif len(option_list) < 2:
            await ctx.send("❌ You need to provide multiple options!")
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
