import nextcord

from source import robot

@robot.event
async def on_ready():
    robot.remove_command("help")

    await robot.change_presence(status=nextcord.Status.dnd)

    print(f"{robot.user.name} has connected to Discord.")
    print(f"Current Event Loop: {robot.loop}")