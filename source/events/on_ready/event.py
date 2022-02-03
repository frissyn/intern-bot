import nextcord

from source import robot

from db import session
from db.models import Ticket

from source.cogs.tickets.views import HelpBoard
from source.cogs.tickets.views import JoinThreadView
from source.cogs.tickets.views import CategoryDropdownView

@robot.event
async def on_ready():
    print(f"{robot.user.name} has connected to Discord.")
    print(f"Current Event Loop: {robot.loop}")

    v = HelpBoard(robot)

    robot.add_view(v)

    for t in session.query(Ticket).all():
        if not t.resolved:
            robot.add_view(CategoryDropdownView(t, v))
            robot.add_view(JoinThreadView(t, robot))

            print(f"Loaded view: <JoinThreadView> {t.f_id()} - {t.client.user_id}")
