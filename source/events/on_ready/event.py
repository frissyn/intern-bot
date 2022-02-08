import nextcord

from source import robot

from db import session
from db.models import Ticket

from source.cogs.tickets.views.ticket import HelpBoardView
from source.cogs.tickets.views.misc import JoinThreadView
from source.cogs.tickets.views.misc import HelpRoleSelectView


@robot.event
async def on_ready():
    print(f"{robot.user.name} has connected to Discord.")
    print(f"Current Event Loop: {robot.loop}")

    robot.add_view(HelpBoardView(robot))
    robot.add_view(HelpRoleSelectView(robot))

    for t in session.query(Ticket).all():
        if not t.resolved:
            robot.add_view(JoinThreadView(t, robot))

            print(f"Loaded view: <JoinThreadView> {t.f_id()} - {t.client.user_id}")
