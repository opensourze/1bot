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

# Command to message a user from 1Bot
@client.command(hidden=True)
@commands.is_owner()
async def messageuser(ctx, id: int, *, message):
    if id in client.owner_ids:
        return await ctx.send(
            "You can't send messages to an owner through 1Bot. why not talk to them directly smh"
        )
    try:
        user: discord.User = client.get_user(id)

        embed = discord.Embed(
            title="My developers have sent you a message!",
            colour=0xFF6600,
        )

        embed.add_field(name="Message", value=message)

        await user.send(embed=embed)
        await ctx.send(f"✅ Warned user `{user.name}` with this embed.", embed=embed)

    except Exception as e:
        await ctx.send(f"❌ **Error:**\n\n{e}")


# Command to ban a user from submitting suggestions
@client.command(hidden=True, aliases=["suggestionban", "suggestionblock"])
@commands.is_owner()
async def block(ctx, id: int, *, reason):
    if id in client.owner_ids:
        return await ctx.send("you can't block an owner dummy")
    try:
        user: discord.User = client.get_user(id)

        embed = discord.Embed(
            title="You've been blocked from sending suggestions!",
            color=0xFF0000,
            description=f"You've been banned from submitting suggestions as we have noticed that you are spamming them.",
        )
        embed.add_field(name="Reason", value=reason, inline=False)

        bans.insert_one({"_id": id})

        await user.send(embed=embed)
        await ctx.send(f"✅ Blocked user `{user.name}` with this embed:", embed=embed)

    except Exception as e:
        await ctx.send(f"❌ **Error:**\n\n{e}")


# Loop through py files in cogs directory and load them
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")

# Load Jishaku
client.load_extension("jishaku")


client.run(os.environ["TOKEN"])
