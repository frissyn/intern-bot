import nextcord

from source import robot

@robot.event
async def on_ready():
    print(f"{robot.user.name} has connected to Discord.")
    print(f"Event Loop: {robot.loop.__name__}")
    print(f"Event Loop Internal Time: {robot.loop.time()}")