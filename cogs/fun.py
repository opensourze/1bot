import os
import random
from asyncio import sleep

import discord
import requests
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from Discord_Together.discordtogether import DiscordTogether


class Fun(commands.Cog, description="Who doesn't want to have some fun?"):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready")

    # Mock text command
    @commands.command(help="Mock text (alternating upper and lower case)")
    async def mock(self, ctx, *, text):
        mock_text = "".join(
            [char.upper() if i % 2 else char.lower() for i, char in enumerate(text)]
        )

        await ctx.send(mock_text)

    @cog_ext.cog_slash(
        name="mock",
        description="Mock text (alternating upper and lower case)",
        guild_ids=[862688794662141993],
    )
    async def mock_slash(self, ctx: SlashContext, *, text):
        await self.mock(ctx, text=text)

    # YouTube Together
    @commands.command(help="Watch YouTube together with friends", aliases=["yt"])
    @commands.guild_only()
    async def youtube(self, ctx, *, vc: commands.VoiceChannelConverter):
        dt = DiscordTogether(token=os.environ["TOKEN"])
        invite_code = await dt.activity(option="youtube", vc_id=vc.id)
        await ctx.send(f"Click to join: <https://discord.com/invite/{invite_code}>")

    @youtube.error
    async def yt_error(self, ctx, error):
        if isinstance(error, commands.ChannelNotFound):
            embed = discord.Embed(
                title=":x: Channel Not Found",
                description=f"Couldn't find that channel. You must type the **exact** name of the channel, "
                + "**which is why it is recommended to use the Slash Command version of this command instead.**\n"
                + "If you are typing a `#` before the name of the channel, **don't**.",
                color=0xFF0000,
            ).set_footer(
                text="Quick tip: If you have developer mode on, you can just use the ID of the voice channel."
            )

            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                ":x: You must specify a voice channel to start the activity in."
            )

    @cog_ext.cog_slash(
        name="youtube_together",
        description="Watch YouTube together in a voice channel",
        options=[
            create_option(
                name="vc",
                description="The voice channel where you want to start the activity",
                required=True,
                option_type=7,
            )
        ],
    )
    async def yt_slash(self, ctx: SlashContext, vc: discord.VoiceChannel):
        await self.youtube(ctx, vc=vc)

    # Dad joke command
    @commands.command(help="Get a random dad joke", brief="Get a random dad joke")
    async def dadjoke(self, ctx):
        json = requests.get(
            "https://official-joke-api.appspot.com/jokes/general/random"
        ).json()[0]
        await ctx.send(f"**{json['setup']}**\n\n{json['punchline']}")

    @cog_ext.cog_slash(name="dadjoke", description="Get a random dad joke")
    async def dadjoke_slash(self, ctx: SlashContext):
        await self.dadjoke(ctx)

    # Programming joke command
    @commands.command(
        help="Get a random programming-related joke",
        brief="Get a programming joke",
        aliases=["codingjoke"],
    )
    async def programmingjoke(self, ctx):
        json = requests.get("https://programming-humor.herokuapp.com/").json()
        await ctx.send(f"**{json['setup']}**\n\n{json['punchline']}")

    @cog_ext.cog_slash(
        name="programmingjoke", description="Get a programming-related joke"
    )
    async def programmingjoke_slash(self, ctx: SlashContext):
        await self.programmingjoke(ctx)

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
            if json["code"]:
                await ctx.send(
                    json["message"]
                )  # Send the error message if there is an error code
                return
        except KeyError:
            if json["nsfw"] == False:
                title = (
                    json["title"][:253] + "..."
                    if len(json["title"]) > 256
                    else json["title"]
                )
                meme_embed = discord.Embed(
                    title=title,
                    color=0xFF6600,
                    url=json["postLink"],
                    description=f"r/{json['subreddit']}",
                )
                meme_embed.set_image(url=json["url"])
                await ctx.send(embed=meme_embed)

        if json["nsfw"]:
            await ctx.send(f":exclamation: Warning: NSFW post!\n\n<{json['postLink']}>")

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
        try:
            await ctx.send(json["results"][0]["url"])
        except IndexError:
            await ctx.send(":x: Couldn't find any matching GIFs.")

    @cog_ext.cog_slash(name="gif", description="Search for GIFs (filtered) on Tenor")
    async def gif_slash(self, ctx: SlashContext, *, query):
        await self.gif(ctx, query=query)

    # 8ball command
    @commands.command(
        help="Ask the magic 8-ball a question", name="8ball", aliases=["eightball"]
    )
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

        random_response = random.choice(responses)

        message = await ctx.send(
            f'Your question was: "{question}"\n\n:8ball: *The magic 8-ball says...*'
        )
        await sleep(2)
        # Edit message and add response after two seconds
        await message.edit(
            content=f'Your question was: "{question}"\n\n:8ball: *The magic 8-ball says...*\n**{random_response}**'
        )

    @cog_ext.cog_slash(
        name="8ball",
        description="Ask the magic 8-ball a question",
        options=[
            create_option(
                name="question",
                description="What do you want to ask?",
                required=True,
                option_type=3,
            )
        ],
    )
    async def eightball_slash(self, ctx: SlashContext, question):
        await self.eightball(ctx, question=question)

    # Coin flip command
    @commands.command(help="Flip a coin", aliases=["coinflip", "flipcoin"])
    async def flip(self, ctx):
        if random.randint(1, 10) <= 5:
            await ctx.send("I flipped a coin for you, it's **heads**!")
        else:
            await ctx.send("I flipped a coin for you, it's **tails**!")

    @cog_ext.cog_slash(name="coinflip", description="Flip a coin")
    async def flip_slash(self, ctx: SlashContext):
        await self.flip(ctx)


# Add cog
def setup(client):
    client.add_cog(Fun(client))
