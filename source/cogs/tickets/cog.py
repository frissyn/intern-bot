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

from .utility import LOYAL
from .utility import TARGET
from .utility import HELPER
from .utility import make_client
from .utility import file_content


class Snowflake_(object):
    def __init__(self, i):
        self.id = i


class Tickets(Base):
    @commands.command("tickets.board")
    async def tickets_board(self, ctx):
        c = file_content("board")
        em = nextcord.Embed(color=COLOR, description=c, title=r"📜 **HELP BOARD**")
        
        await ctx.send(embed=em, view=HelpBoard(self.bot))

    @commands.command("tickets.blacklist", aliases=["tbl"])
    async def tickets_blacklist(self, ctx, mem: nextcord.Member, duration: int):
        c = make_client(mem.id)

        if c.blacklisted:
            return await ctx.send(
                f"**{mem.name}** is already blacklisted "
                f"for {c.bl_delta().seconds // 3600} remaining hours."
            )

        c.blacklist(hours=int(duration), perma=False)
        session.commit()

        await ctx.send(
            f"**{mem.name}** has been blacklisted from creating new help "
            f"threads for **{duration}** hours."
        )
    
    @commands.command("tickets.helper")
    async def tickets_helper(self, ctx):
        if not ctx.author.get_role(LOYAL): return

        helper = Snowflake_(HELPER)

        if HELPER in [r.id for r in ctx.author.roles]:
            await ctx.author.remove_roles(helper)
        else:
            await ctx.author.add_roles(helper)

        await ctx.message.add_reaction("👍")
    
    @commands.command("tickets.permaban", aliases=["tban"])
    async def tickets_permaban(self, ctx, mem: nextcord.Member):
        c = make_client(mem.id)

        c.blacklist(hours=0, perma=True)
        session.commit()

        await ctx.send(
            f"**{mem.name}** has been permanantely blacklisted from "
            "creating new help threads."
        )
    
    @commands.command("tickets.resolve", aliases=["resolve"])
    async def tickets_resolve(self, ctx):
        c = make_client(ctx.author.id)
        ticket = session.query(Ticket).filter_by(thread_id=ctx.channel.id).first()

        if not ticket: return
        if ticket.client_id != c.user_id: return

        ticket.resolve()
        session.commit()

        em = nextcord.Embed(color=COLOR)
        em.description = "Use **[this link](https://discord.com/"
        em.description += f"channels/{ctx.guild.id}/{ctx.channel.id}/)** to "
        em.description += "refer to this thread in the future. Make sure to "
        em.description += "bookmark it if you need to!"
        em.set_footer(text=f"Ticket ID: {ticket.f_id()} | Opened: {ticket.stamp}")

        target = self.bot.get_channel(TARGET)
        m = await target.fetch_message(ticket.notice_id)

        await m.edit(view=ResolvedThreadView())
        await ctx.send("This thread has been marked as resolved.", embed=em)
        await ctx.channel.edit(archived=True, locked=True)
    
    @commands.command("tickets.force_allow", aliases=["tfa"])
    async def tickets_force_allow(self, ctx, m: nextcord.Member):
        c = make_client(m.id)

        c.whitelist()
        c.force_last_used()
        session.commit()

        await ctx.send(f"Forced ticket creation perms for **{m.name}**.")
    
    @commands.command("tickets.force_resolve", aliases=["force_resolve", "tfr"])
    async def tickets_force_resolve(self, ctx):
        ticket = session.query(Ticket).filter_by(thread_id=ctx.channel.id).first()

        if not ticket: return

        ticket.resolve()
        session.commit()

        em = nextcord.Embed(color=COLOR)
        em.description = "Use **[this link](https://discord.com/"
        em.description += f"channels/{ctx.guild.id}/{ctx.channel.id}/)** to "
        em.description += "refer to this thread in the future. Make sure to "
        em.description += "bookmark it if you need to!"
        em.set_footer(text=f"Ticket ID: {ticket.f_id()} | Opened: {ticket.stamp}")

        target = self.bot.get_channel(TARGET)
        m = await target.fetch_message(ticket.notice_id)

        await m.edit(view=ResolvedThreadView())
        await ctx.send("This thread has been marked as resolved.", embed=em)
        await ctx.channel.edit(archived=True, locked=True)

    @commands.command("tickets.whitelist", aliases=["twl"])
    async def tickets_whitelist(self, ctx, m: nextcord.Member):
        c = make_client(m.id)

        c.whitelist()
        session.commit()

        await ctx.send(f"**{m.name}** has been whitelisted.")

    @commands.command("tickets.unresolved", aliases=["tshow"])
    async def tickets_unresolved(self, ctx):
        tickets = session.query(Ticket).filter_by(resolved=False).all()

        em = nextcord.Embed(color=COLOR, description="")
        em.title = f"Found {len(tickets)} unresolved tickets"
        
        for t in tickets:
            em.description += f"<@{t.client.user_id}> | <#{t.thread_id}> - "
            em.description += f"[Notice Board](https://discord.com/channels/"
            em.description += f"437048931827056642/{t.thread_id}/{t.notice_id})\n"
        
        await ctx.send(embed=em)
