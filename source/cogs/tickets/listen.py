import nextcord

from db import session
from db.models import Ticket

from source import COLOR
from source.cogs.cog import Base

from nextcord.ext import commands

from .utility import TARGET
from .utility import LOGGER
from .utility import increment_notice


class TicketsEvents(Base):
    @commands.Cog.listener()
    async def on_thread_member_join(self, member):
        m = await self.ticket_notice(member.thread_id)

        if not m: return
        await increment_notice(m, 1)

    @commands.Cog.listener()
    async def on_thread_member_remove(self, member):
        m = await self.ticket_notice(member.thread_id)

        if not m: return
        await increment_notice(m, -1)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.channel.id == TARGET:
            if msg.is_system():
                await msg.delete(delay=5)
    
    async def on_blacklist(self, mem, duration, reason):
        for c in LOGGER:
            target = self.bot.get_channel(c)

            if not duration:
                descrip = (
                    f"**{mem.name}** has been permantely blacklisted from "
                    f"creating new help tickets. \n\n**Reason:** *{reason}*"
                )
            else:
                descrip = (
                    f"**{mem.name}** has been blacklisted from creating new "
                    f"help tickets for **{duration}** hours. \n\n**Reason:** *{reason}*"
                )

            await target.send(
                f"<@{mem.id}>",
                embed=nextcord.Embed(color=COLOR, title="Help Thread Blacklist", description=descrip),
                allowed_mentions=nextcord.AllowedMentions.all()
            )
    
    
    async def on_ticket_create(self, user, ticket):
        target = self.bot.get_channel(LOGGER[0])

        em = nextcord.Embed(title="New Ticket Created", color=COLOR)
        em.description = f"**Client:** {user.mention}\n"
        em.description += f"**Type:** {ticket.type_}\n"
        em.description += f"**Thread:** <#{ticket.thread_id}>"
        em.set_footer(text=f"Ticket ID: {ticket.f_id()} | Opened: {ticket.stamp}")

        await target.send(embed=em)

    async def ticket_notice(self, thread_id: int):
        ticket = session.query(Ticket).filter_by(thread_id=thread_id).first()

        if not ticket: return None
        if not ticket.notice_id: return None

        target = self.bot.get_channel(TARGET)
        m = await target.fetch_message(ticket.notice_id)

        return m
