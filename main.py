# This is the file to run. It also contains the commands to warn/ban users from 1Bot

print("Bot written by @opensourze")

import os

import discord
import dotenv
from certifi import where
from discord.ext import commands
from discord_slash import SlashCommand
from pymongo import MongoClient

from client import Client

dotenv.load_dotenv()

cluster = MongoClient(os.environ["MONGO_URL"], tlsCAFile=where())
bans = cluster["1bot"]["bans"]

client = Client()
slash = SlashCommand(client, sync_commands=True, delete_from_unused_guilds=True)

# Command to warn a user from 1Bot
@client.command(hidden=True)
@commands.is_owner()
async def botwarn(ctx, id: int, *, message):
    if id in client.owner_ids:
        return await ctx.send("you can't ban an owner smh")
    try:
        user: discord.User = client.get_user(id)

        embed = discord.Embed(
            title="Global warning",
            colour=0xFF0000,
            description="You have received a warning from 1Bot's team.",
        )

        embed.add_field(name="Message", value=message)
        embed.set_footer(
            text="If we feel like, we can ban you from using 1Bot entirely; on all servers and DMs."
        )

        await user.send(embed=embed)
        await ctx.send(f"✅ Warned user `{user.name}` with this embed.", embed=embed)

    except Exception as e:
        await ctx.send(f"❌ **Error:**\n\n{e}")


# Command to ban a user from 1Bot
@client.command(hidden=True)
@commands.is_owner()
async def botban(ctx, id: int, *, reason):
    try:
        user: discord.User = client.get_user(id)

        embed = discord.Embed(
            title="You've been BANNED from 1Bot!",
            color=0xFF0000,
            description=f"You've been banned from using 1Bot on **all servers and DMs.**",
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(
            name="Appeal",
            value="Remember, if you spam these socials, you'll be blocked there too.\n"
            + "[Twitter](https://twitter.com/opensourze)\n"
            + "[Keybase](https://keybase.io/opensourze)\n"
            + "[GitHub](https://github.com/opensourze/1bot/issues/new) (use the `Ban appeal` label)\n"
            + "[Reddit](https://reddit.com/user/opensourze)",
            inline=False,
        )

        bans.insert_one({"_id": id})

        await user.send(embed=embed)
        await ctx.send(f"✅ Banned user `{user.name}` with this embed.", embed=embed)

    except Exception as e:
        await ctx.send(f"❌ **Error:**\n\n{e}")


# Loop through py files in cogs directory and load them
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")

# Load Jishaku
client.load_extension("jishaku")


client.run(os.environ["TOKEN"])
