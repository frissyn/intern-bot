import nextcord

from source import robot

@robot.event
async def on_connect():
    robot.remove_command("help")
    await robot.change_presence(status=nextcord.Status.dnd)