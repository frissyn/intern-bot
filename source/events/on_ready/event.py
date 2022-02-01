import nextcord

from source import robot


@robot.event
async def on_ready():
    print(f"{robot.user.name} has connected to Discord.")
    print(f"Current Event Loop: {robot.loop}")
