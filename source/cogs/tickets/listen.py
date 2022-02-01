import re
import nextcord

from db import session
from db.models import Ticket

from source.cogs.cog import Base

from nextcord.ext import tasks
from nextcord.ext import commands

from .utility import TARGET

from .views import HelpBoard
from .views import JoinThreadView
from .views import ResolvedThreadView
from .views import CategoryDropdownView


TEST = "xxx users are currently in this help thread."


class TicketsEvents(Base):
    async def ticket_notice(self, thread_id: int):
        ticket = session.query(Ticket).filter_by(thread_id=thread_id).first()

        if not ticket: return None
        if not ticket.notice_id: return None

        target = self.bot.get_channel(TARGET)
        m = await target.fetch_message(ticket.notice_id)

        return m
    
    async def increment_notice(self, msg: nextcord.Message, count):
        em = msg.embeds[0]
        num = re.findall(r"\d+", em.description)[0]
        em.description = (
            em.description[:len(TEST)] +
            em.description[len(TEST):].replace(num, str(int(num) + count))
        )

        await msg.edit(embed=em)

    @commands.Cog.listener()
    async def on_ready(self):
        v = HelpBoard(self.bot)

        self.bot.add_view(v)

        for t in session.query(Ticket).all():
            self.bot.add_view(JoinThreadView(t, self.bot))

            if not t.resolved:
                self.bot.add_view(CategoryDropdownView(t, v))

    @commands.Cog.listener()
    async def on_thread_member_join(self, member):
        m = await self.ticket_notice(member.thread_id)

        if not m: return
        await self.increment_notice(m, 1)

    @commands.Cog.listener()
    async def on_thread_member_remove(self, member):
        m = await self.ticket_notice(member.thread_id)

        if not m: return
        await self.increment_notice(m, -1)

    @tasks.loop(seconds=float(60*5))
    async def notice_check(self):
        tickets = session.query(Ticket).filter_by(resolved=False)

        for t in tickets:
            thread = self.bot.get_channel(t.thread_id)

            if thread.archived:
                m = await self.ticket_notice(t.id)

                if m:
                    await m.edit(view=ResolvedThreadView())
    
    @notice_check.before_loop
    async def before_notice_check(self):
        await self.bot.wait_until_ready()
