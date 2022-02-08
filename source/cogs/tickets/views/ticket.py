import asyncio
import nextcord

from nextcord import ui

from source import COLOR

from db import session
from db.models import Ticket
from db.models import Context

from .misc import ConfirmView
from .misc import JoinThreadView
from .misc import CategoryDropdownView

from ..utility import TARGET
from ..utility import HELPER
from ..utility import make_client
from ..utility import file_content


class HelpBoardView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.target = TARGET

    @nextcord.ui.button(label="Code Help", custom_id="ps:cod", emoji=r"💳")
    async def code_button(self, *args, **kwargs):
        await self.handle_click(*args, **kwargs)

    @nextcord.ui.button(label="Replit Help", custom_id="ps:rep", emoji=r"🖥️")
    async def replit_button(self, *args, **kwargs):
        await self.handle_click(*args, **kwargs)

    @nextcord.ui.button(label="Bot Help", custom_id="ps:bot", emoji=r"🤖")
    async def bot_button(self, *args, **kwargs):
        await self.handle_click(*args, **kwargs)

    async def handle_click(self, btn, inter):
        res = inter.response
        client = make_client(inter.user.id)
        can_open, reason = client.can_open()

        if not can_open:
            return await res.send_message(reason, ephemeral=True)
        else:
            view = ConfirmView()

            await res.send_message(
                f"Do you really want to create a **{btn.label}** ticket?",
                view=view, ephemeral=True
            )

            await view.wait()

            if view.value in [None, False]:
                return 
            else:
                client.opened()
                session.commit()

        target = self.bot.get_channel(self.target)
        thread = await target.create_thread(
            auto_archive_duration=1440,
            name=f"ticket-{inter.user.name}",
            type=nextcord.ChannelType.public_thread,
            reason=f"Auto-created thread for {btn.label} ticket from {inter.user.name}"
        )

        ticket = Ticket(body=None, type_=btn.label, client_id=client.id, thread_id=thread.id)
        ticket.add_self(session)
        session.commit()

        await thread.edit(name=f"{thread.name} | {ticket.f_id()}")
        await self.bot.cogs["TicketsEvents"].on_ticket_create(inter.user, ticket)

        c = file_content("thread")
        check = lambda m: m.author.id == inter.user.id
        em = nextcord.Embed(title=f"{btn.label} Thread", description=c, color=COLOR)
        em.set_footer(text=f"Ticket ID: {ticket.f_id()} | Opened: {ticket.stamp}")

        await thread.add_user(inter.user); await thread.send(embed=em)

        try:
            m = await self.bot.wait_for("message", check=check, timeout=60 * 5)
        except asyncio.TimeoutError:
            await thread.send("Timed out while waiting for response. Archiving thread.")
            await thread.edit(archived=True, locked=True)

            ticket.update(resolved=True, body="error:asyncio.TimeoutError")
            session.commit()

            return True

        ticket.update(body=m.content)
        session.commit()

        for a in m.attachments:
            c = Context(url=a.url, type_=a.content_type, ticket_id=ticket.id)
            c.add_self(session)

        session.commit()

        await m.pin(reason=f"Pinned ticket body for {thread.name}")

        if btn.label != "Replit Help":
            async def check(x):
                return x == inter.user.id

            view = CategoryDropdownView(check)

            dropdown = await thread.send(
                "Got it! Please select all the categories that apply "
                "to your question. (No more than 3). Your question "
                "doesn't fit what's listed? Select 'Miscellaneous'!",
                view=view
            )

            await view.wait()
            await dropdown.delete()
            values = view.values if view.values is not None else []
        else:
            values = ["help-replit"]
        
        roles = [r for r in thread.guild.roles if r.name in values]
        cats = [r.replace("help-", "") for r in values]

        em = nextcord.Embed(color=COLOR)

        if len(ticket.body) >= 240:
            body, el = ticket.body[:240].replace('\n', ''), "..."
        else:
            body, el = ticket.body.replace('\n', ''), ""

        em.title=f"**New {ticket.type_} Request!**"
        em.description = f"<@{inter.user.id}> asks, \"{body}{el}\"\n "
        em.description += f"**Categories**: {' '.join(cats)}\n\n"
        em.description += f"**1** users are currently in this help thread. "
        em.set_footer(text=f"Ticket ID: {ticket.f_id()} | Opened: {ticket.stamp}")


        msg = await target.send(
            f"{' '.join([r.mention for r in roles])}",
            embed=em,
            allowed_mentions=nextcord.AllowedMentions.all(),
            view=JoinThreadView(ticket, self.bot)
        )

        ticket.update(notice_id=msg.id)
        session.commit()

        await thread.edit(locked=False)
        await inter.message.delete()
        await thread.send(
            "Your ticket has been saved. Help will join the thread soon! "
            "Once you have recieved satisfactory help, use `%resolve` "
            "so I know to archive the thread and mark your question as resolved."
        )

        role = inter.guild.get_role(HELPER)

        await thread.send(
            f"[Ticket {ticket.f_id()}] (Auto Mention: {role.mention})",
            delete_after=1,
            allowed_mentions=nextcord.AllowedMentions.all()
        )
