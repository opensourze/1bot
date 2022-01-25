import asyncio
import base64
import binascii
from contextlib import suppress

import discord
import requests
from discord.ext import commands
from discord.utils import escape_markdown
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from temperature_converter_py import celsius_to_fahrenheit, fahrenheit_to_celsius
from utils import Pager


class Utilities(commands.Cog, description="A set of useful utility commands."):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.emoji = "<:utilities:907550185629040680>"

    # Celsius to Fahrenheit
    @commands.command(help="Convert Celsius to Fahrenheit", aliases=["c2f", "ctof"])
    async def celsiustofahrenheit(self, ctx, *, temperature: float):
        await ctx.send(
            f"{temperature}°C is {round(celsius_to_fahrenheit(temperature), 2)}°F"
        )

    @cog_ext.cog_slash(
        name="celsius-to-fahrenheit", description="Convert Celsius to Fahrenheit"
    )
    async def c2f_slash(self, ctx: SlashContext, *, temperature: float):
        await self.celsiustofahrenheit(ctx, temperature=temperature)

    # Fahrenheit to Celsius
    @commands.command(help="Convert Fahrenheit to Celsius", aliases=["f2c", "ftoc"])
    async def fahrenheittocelsius(self, ctx, *, temperature: float):
        await ctx.send(
            f"{temperature}°F is {round(fahrenheit_to_celsius(temperature), 2)}°C"
        )

    @cog_ext.cog_slash(
        name="fahrenheit-to-celsius", description="Convert Fahrenheit to Celsius"
    )
    async def f2c_slash(self, ctx: SlashContext, *, temperature: float):
        await self.fahrenheittocelsius(ctx, temperature=temperature)

    # Calc command
    @commands.command(
        help="Run a math operation with two numbers. Separate the numbers and the operation by spaces.",
        brief="A simple calculator with two numbers",
        aliases=["calculate", "calculator"],
    )
    async def calc(self, ctx, num_1: float, operation: str, num_2: float):
        o = operation.lower()

        if o == "+" or o == "plus":
            return await ctx.send(str(num_1 + num_2))
        if o == "-" or o == "minus":
            return await ctx.send(str(num_1 - num_2))
        if o == "*" or o == "times" or o == "x":
            return await ctx.send(str(num_1 * num_2))
        if o == "/" or o == "by":
            try:
                return await ctx.send(str(num_1 / num_2))
            except ZeroDivisionError:
                await ctx.send("❌ You can't divide by zero!")
        else:
            await ctx.send(
                "❌ Invalid operation. Use one of these for the operation: `+, plus, -, minus, *, x, /`"
            )

    @cog_ext.cog_slash(
        name="calculate",
        description="Run a math operation with two numbers",
        options=[
            create_option(
                name="num_1",
                description="The first number (can be decimal)",
                required=True,
                option_type=3,
            ),
            create_option(
                name="operation",
                description="Choose between: + - x /",
                required=True,
                option_type=3,
            ),
            create_option(
                name="num_2",
                description="The second number (can be decimal)",
                required=True,
                option_type=3,
            ),
        ],
    )
    async def calc_slash(self, ctx: SlashContext, num_1, operation, num_2):
        try:
            await self.calc(ctx, float(num_1), operation, float(num_2))
        except:
            await ctx.send("❌ Please use valid numbers!")

    # Emoji command
    @commands.command(
        name="emoji",
        aliases=["createemoji", "addemoji", "emote"],
        help="Create a custom emoji on this server",
    )
    @commands.has_permissions(manage_emojis=True)
    @commands.bot_has_permissions(manage_emojis=True)
    async def emoji_cmd(self, ctx, emoji_name: str, *, image_link: str = None):
        with suppress(AttributeError):
            if not ctx.message.attachments and not image_link:
                return await ctx.send(
                    f"❌ You need to attach an image or provide an image link to create an emoji."
                )

        try:
            if image_link:
                image = requests.get(image_link).content
            else:
                image = await ctx.message.attachments[0].read()

            created_emoji = await ctx.guild.create_custom_emoji(
                name=emoji_name, image=image
            )

            await ctx.send(f"✅ Emoji created! {created_emoji}")

        # errors
        except discord.HTTPException as e:
            if "File cannot be larger than 256" in str(e):
                await ctx.send(
                    "❌ That image is too big for an emoji. Use an image that is smaller than 256 kb (you can try <https://squoosh.app> to compress it)."
                )
            elif "String value did not match validation regex" in str(e):
                await ctx.send(
                    "❌ Invalid emoji name; you have unsupported characters in the emoji name."
                )
            elif "Must be between 2 and 32 in length" in str(e):
                await ctx.send("❌ The emoji name must be 2 to 32 characters long.")
            elif "Maximum number of emojis reached" in str(e):
                await ctx.send(
                    "❌ This server has reached its emoji limit.\n"
                    + "You'll have to boost the server to the next level to get more emoji slots!"
                )

            return
        except Exception as e:
            request_errs = requests.exceptions

            if isinstance(
                e,
                (
                    request_errs.MissingSchema,
                    request_errs.InvalidSchema,
                    request_errs.ConnectionError,
                    discord.InvalidArgument,
                ),
            ):
                await ctx.send(
                    "❌ Invalid image. Please provide a valid image attachment or URL."
                )

    @cog_ext.cog_slash(
        name="emoji",
        description="Create a custom emoji on this server",
        options=[
            create_option(
                name="emoji_name",
                description="The name of the emoji",
                required=True,
                option_type=3,
            ),
            create_option(
                name="image_link",
                description="The URL of the image to create an emoji from.",
                required=True,
                option_type=3,
            ),
        ],
    )
    @commands.has_permissions(manage_emojis=True)
    async def emoji_slash(self, ctx: SlashContext, emoji_name, image_link):
        await self.emoji_cmd(ctx, emoji_name, image_link=image_link)

    # Raw text command
    @commands.command(
        aliases=["rawtext"],
        help="Get the raw, unformatted text of the message you replied to. You can also use a message ID.",
        brief="Get raw text of the message you replied to.",
    )
    async def raw(self, ctx, message_id: str = None):
        message = None  # gets reassigned after message is fetched

        try:
            # try fetching the replied message
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if message is None:
                return await ctx.send(
                    "❌ This message could not be fetched, or it might not have text content."
                )
        except (discord.NotFound, AttributeError):  # if the message is not a reply
            if not message_id:
                return await ctx.send(
                    "❌ You need to either reply to a message with this command or provide a message ID!"
                )

            try:
                message = await ctx.channel.fetch_message(message_id)
            except discord.NotFound:
                return await ctx.send(
                    "❌ The message you provided was not found in this channel!"
                )

        if not message.content:
            await ctx.send("❌ This message has no content.")
            return

        embed = discord.Embed(
            description=escape_markdown(message.content), colour=self.client.colour
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="raw",
        description="Get raw text of a message with its ID",
        options=[
            create_option(
                name="message_id",
                description="The ID of the message to get raw text from",
                required=True,
                option_type=3,
            )
        ],
    )
    async def raw_slash(self, ctx: SlashContext, message_id):
        await self.raw(ctx, message_id=message_id)

    # Search repositories
    @commands.command(
        help="Search for a GitHub repository",
        aliases=["searchrepo", "githubsearch"],
    )
    async def github(self, ctx, *, search_query):
        json = requests.get(
            f"https://api.github.com/search/repositories?q={search_query}"
        ).json()

        if json["total_count"] == 0:
            await ctx.send("No matching repositories found")
        else:
            await ctx.send(
                f"First result for '{search_query}':\n{json['items'][0]['html_url']}"
            )

    @cog_ext.cog_slash(
        name="search_github", description="Search for repositories on GitHub"
    )
    async def github_slash(self, ctx: SlashContext, *, query):
        await self.github(ctx, query=query)

    # PyPI command
    @commands.command(help="Get info for a PyPI module")
    async def pypi(self, ctx, *, package):
        # Get package JSON
        res = requests.get(f"https://pypi.org/pypi/{package}/json")

        if res.status_code == 404:
            # Exit with an error message if status is 404 (not found)
            await ctx.send("❌ That module doesn't exist!")
            return

        json = res.json()

        embed = discord.Embed(
            title=json["info"]["name"],
            colour=self.client.colour,
            url=json["info"]["package_url"],
        )

        if json["info"]["summary"] != "UNKNOWN":
            embed.description = json["info"]["summary"]

        # Max length for embed fields is 1024
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

        if json["info"]["license"]:
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
                colour=0xD50000,
                url="https://www.npmjs.com/package/" + package,
            )

            with suppress(KeyError):
                embed.description = json["description"]
            with suppress(KeyError):
                embed.add_field(name="Homepage", value=json["homepage"], inline=False)
            with suppress(KeyError):
                embed.add_field(name="Author", value=json["author"]["name"])
            with suppress(KeyError):
                embed.add_field(
                    name="GitHub repository",
                    # Remove "git+" and ".git" from the url
                    value=json["repository"]["url"],
                    inline=False,
                )
            embed.add_field(
                name="Repository maintainers",
                value=", ".join(
                    maintainer["name"] for maintainer in json["maintainers"]
                ),
                inline=False,
            )
            with suppress(KeyError):
                embed.add_field(name="License", value=json["license"], inline=False)

            await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="npm", description="Get info for an NPM module")
    async def npm_slash(self, ctx: SlashContext, *, package):
        await self.npm(ctx, package=package)

    # Lyrics command
    @commands.command(help="Get lyrics for a song", aliases=["ly"])
    async def lyrics(self, ctx, *, song):
        with suppress(AttributeError):
            await ctx.trigger_typing()

        json = requests.get(f"https://some-random-api.ml/lyrics?title={song}").json()

        with suppress(KeyError):
            if json["error"]:
                await ctx.send("❌ " + json["error"])
                return

        pager = Pager(
            title=json["title"],
            thumbnail=json["thumbnail"]["genius"],
            timeout=100,
            entries=[
                json["lyrics"][i : i + 700] for i in range(0, len(json["lyrics"]), 700)
            ],
            length=1,
            colour=self.client.colour,
        )

        await pager.start(ctx)

    @cog_ext.cog_slash(name="lyrics", description="Get lyrics for a song")
    async def lyrics_slash(self, ctx: SlashContext, *, song):
        await self.lyrics(ctx, song=song)

    # Base64 commands
    @commands.group(
        invoke_without_command=True, help="Encode/decode base64", aliases=["b64"]
    )
    async def base64(self, ctx):
        embed = discord.Embed(
            title="Base64 commands",
            description="Run `1 base64 e {text}` to convert the text into base64.\n"
            + "Run `1 base64 d {base64}` to decode base64 code.\n",
            colour=self.client.colour,
        ).set_footer(text="Don't include the brackets while running commands!")

        await ctx.send(embed=embed)

    @base64.command(help="Encode text into base64", aliases=["e"])
    async def encode(self, ctx, *, text):
        embed = discord.Embed(
            title="Encoded Base64 code",
            description=escape_markdown(base64.b64encode(text.encode()).decode()),
            colour=self.client.colour,
        )
        embed.set_footer(text=f"Encoded by {ctx.author}")

        await ctx.send(embed=embed)

    @base64.command(help="Decode base64 into text", aliases=["d"])
    async def decode(self, ctx, *, code):
        try:
            embed = discord.Embed(
                title="Decoded Base64 text",
                description=escape_markdown(base64.b64decode(code).decode()),
                colour=self.client.colour,
            )
            embed.set_footer(text=f"Decoded by {ctx.author}")
            await ctx.send(embed=embed)
        except binascii.Error:
            await ctx.send("❌ Invalid code! Are you sure that's base64?")

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
        help="Get weather info for a city",
    )
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def weather(self, ctx, *, query):
        req = requests.get(f"https://api.popcat.xyz/weather?q={query}")
        json = req.json()

        # If json is an empty array (occurs when query is invalid), send an error message
        if json == []:
            return await ctx.send(
                "❌ Couldn't find the city you specified. Please check for typos."
            )

        data = json[0]

        embed = discord.Embed(
            colour=self.client.colour, description=data["current"]["skytext"]
        )
        embed.set_author(
            icon_url=data["current"]["imageUrl"],
            name=f"Weather in {data['location']['name']}",
        )

        embed.add_field(
            name="Temperature",
            value=f'{data["current"]["temperature"]}°{data["location"]["degreetype"]}',
        )
        embed.add_field(
            name="Feels like",
            value=f"{data['current']['feelslike']}°{data['location']['degreetype']}",
        )
        embed.add_field(
            name="Wind",
            value=data["current"]["winddisplay"],
            inline=False,
        )
        embed.add_field(
            name="Humidity",
            value=f"{data['current']['humidity']}%",
        )
        embed.add_field(
            name="Alerts",
            value=data["location"]["alert"] or "No alerts for this area",
            inline=False,
        )

        await ctx.send(embed=embed)

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
            with suppress(AttributeError):
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
    async def poll(self, ctx, question, *, options=None):
        if len(question) > 256:
            return await ctx.send(
                "❌ Your question is too long. Try again with a question shorter than 256 characters!"
            )

        if options:
            numbers = (
                "1️⃣",
                "2️⃣",
                "3️⃣",
                "4️⃣",
                "5️⃣",
                "6️⃣",
                "7️⃣",
                "8️⃣",
                "9️⃣",
                "🔟",
            )

            option_list = options.split("/")

            if len(option_list) > 10:
                return await ctx.send("❌ You cannot have more than 10 choices.")
            if len(option_list) < 2:
                return await ctx.send(
                    '❌ Usage: `poll "Question in quotes" options/separated/by slashes`.\nLeave the options blank for a yes/no poll.'
                )

            embed = discord.Embed(
                title=question,
                colour=self.client.colour,
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

        else:
            embed = discord.Embed(
                title=question,
                colour=self.client.colour,
                description="👍 Yes\n\n👎 No",
            ).set_footer(text=f"Poll created by {str(ctx.author.name)}")

            poll_msg = await ctx.send(embed=embed)
            await poll_msg.add_reaction("👍")
            await poll_msg.add_reaction("👎")

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
                description="The choices you want for the poll separated by slashes (skip this for a yes/no poll)",
                required=False,
                option_type=3,
            ),
        ],
    )
    async def poll_slash(self, ctx, question, options=None):
        await self.poll(ctx, question, options=options)


# Add cog
def setup(client):
    client.add_cog(Utilities(client))
