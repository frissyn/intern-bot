import nextcord

from source import COLOR
from source.cogs.cog import Base

from nextcord.ext import commands

from db import session
from db.models import Ticket
from db.models import Client
from db.models import Context

from .views import HelpBoard
from .views import JoinThreadView
from .views import ResolvedThreadView
from .views import CategoryDropdownView

from .utility import TARGET
from .utility import make_client
from .utility import file_content


class Tickets(Base):
    @commands.Cog.listener()
    async def on_ready(self):
        v = HelpBoard(self.bot)

        self.bot.add_view(v)

        for t in session.query(Ticket).all():
            self.bot.add_view(JoinThreadView(t, self.bot))

            if not t.resolved:
                self.bot.add_view(CategoryDropdownView(t, v))

    @commands.command("tickets.board")
    async def tickets_board(self, ctx):
        c = file_content("board")
        em = nextcord.Embed(color=COLOR, description=c, title=r"📜 **HELP BOARD**")
        
        await ctx.message.delete()
        await ctx.send(embed=em, view=HelpBoard(self.bot))

    @commands.command("tickets.blacklist")
    async def tickets_blacklist(self, ctx, mem: nextcord.Member, duration: int):
        c = make_client(mem.id)

        if c.blacklisted:
            return await ctx.send(
                f"**{mem.name}** is already blacklisted "
                f"for {c.bl_delta().seconds // 3600} remaining hours."
            )

        c.blacklist(int(duration))
        session.commit()

        await ctx.send(
            f"**{mem.name}** has been blacklisted from creating new help "
            f"threads for **{duration}** hours."
        )
    
    @commands.command("tickets.resolve")
    async def tickets_resolve(self, ctx):
        c = make_client(ctx.author.id)
        ticket = session.query(Ticket).filter_by(thread_id=ctx.channel.id).first()

        if not ticket:return
        if ticket.client.id != c.id: return
        
        ticket.resolve()
        session.commit()

        em = nextcord.Embed(color=COLOR)
        em.description = "Use **[this link](https://discord.com/"
        em.description += f"channels/{ctx.guild.id}/{ctx.channel.id}/)** to "
        em.description += "refer to this thread in the future."
        em.set_footer(text=f"Ticket ID: {ticket.f_id()} | Opened: {ticket.stamp}")

        thread =  self.bot.get_channel(ctx.channel.id)

        await thread.edit(archived=True, locked=True, invitable=False)
        await ctx.send("Your thread has been marked as resolved!", embed=em)

        target = self.bot.get_channel(TARGET)
        m = await target.fetch_message(ticket.notice_id)

        await m.edit(view=ResolvedThreadView())

    @commands.command("tickets.unresolved")
    async def tickets_unresolved(self, ctx):
        pass

    @commands.command("tickets.whitelist")
    async def tickets_whitelist(self, ctx, m: nextcord.Member):
        c = make_client(m.id)

        c.whitelist()
        session.commit()

        await ctx.send(f"**{m.name}** has been whitelisted.")
    
    @commands.command("tickets.force_allow")
    async def tickets_allow_open(self, ctx, m: nextcord.Member):
        c = make_client(m.id)

        c.whitelist()
        c.force_last_used()
        session.commit()

        await ctx.send(f"Forced ticket creation perms for **{m.name}**.")
