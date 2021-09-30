# This is the file to run

print("Bot written by @opensourze")

import os

import dotenv
from discord_slash import SlashCommand

from client import Client

dotenv.load_dotenv()

client = Client()
slash = SlashCommand(client, sync_commands=True, delete_from_unused_guilds=True)


# Loop through all files in cogs directory and load them
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")

# Load Jishaku
client.load_extension("jishaku")


client.run(os.environ["TOKEN"])
