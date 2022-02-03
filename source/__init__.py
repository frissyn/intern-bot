import os
import nextcord

from nextcord.ext import commands

COLOR = 0xF2DB94
TOKEN = os.environ["TOKEN"]
INTENTS = nextcord.Intents.all()

robot = commands.Bot(command_prefix="%", intents=INTENTS)
extensions = {
    "events": ["on_ready"],
    "cogs": [
        "clashes",
        "dump",
        "help",
        "sandbox",
        "tickets",
        "utility"
    ],
}

robot.remove_command("help")

for key, values in extensions.items():
    for target in values:
        robot.load_extension(f"source.{key}.{target}")
