import nextcord

from ..cog import Base

from .views import ClashView
from .views import ArchivedClashView

from db import session

from source import COLOR

from nextcord.ext import commands

from db.models import Round
from db.models import Player
from db.models import StaleView
from db.models import Tournament

from db.utility import commit
from db.utility import embed_object


class Clashes(Base):
    def tournament(self, value):
        try:
            value = int(value)
            t = session.query(Tournament).get(value)
        except ValueError:
            if value is True:
                t = session.query(Tournament).filter_by(active=value).first()
            else:
                t = session.query(Tournament).filter_by(title=value).first()
        
        return t


    @commands.command("poll.new")
    async def poll_new(self, ctx, title: str, link: str, active: int):
        t = commit(
            Tournament(
                title=title,
                link=link[1:-1],
                active=bool(active)
            )
        )[0]

        em = embed_object(t, color=COLOR)
        em.title = "Created a new Tournament!"

        await ctx.send(embed=em)
    
    @commands.command("poll.show")
    async def poll_show(self, ctx, value):
        t = self.tournament(value)
        
        if t is None:
            await ctx.message.add_reaction("❓")
        else:
            await ctx.send(embed=embed_object(t, color=COLOR))
    
    @commands.command("poll.link")
    async def poll_link(self, ctx):
        t = self.tournament(True)

        if t is None:
            await ctx.message.add_reaction("❓")
        else:
            await ctx.send(t.link)
    
    @commands.command("poll.new-round")
    async def poll_new_round(self, ctx, value: str, rnum, p: str, rtype: str):
        t = self.tournament(value)

        if t is None:
            await ctx.message.add_reaction("❓")
            return
        
        r = commit(Round(
            tourn_id=t.id,
            rnum=int(rnum),
            rtype=rtype.title()
        ))[0]

        pnames = p.split(" v. ")
        commit(
            Player(name=pnames[0], round_id=r.id),
            Player(name=pnames[1], round_id=r.id)
        )

        em = embed_object(r, color=COLOR)
        em.title = "Created a new Tournament Round!"

        await ctx.send(embed=em)
    
    @commands.command("poll.spawn")
    async def poll_spawn(self, ctx, tid: int, rnum: int):
        t = self.tournament(tid)
        rn = session.query(Round).filter_by(tourn_id=tid, rnum=rnum).first()

        em = nextcord.Embed(color=COLOR)
        em.title = f"{t.title} - Round {rn.rnum}"
        em.description = f"\n:comet: **{rn.players[0].name}** vs. "
        em.description += f":boom: **{rn.players[1].name}**\n\n"
        em.description += "*Interaction failed? Ping <@495609014886072320> "
        em.description += "in <#616645516700155904> for a fix!*"

        view = ClashView(t, rn)
        m = await ctx.send(embed=em, view=view)

        self.bot.add_view(view, message_id=m.id)
        
    @commands.command(name="poll.kill")
    async def kill(self, ctx, *, msgs):
        args = msgs.split(' ')
        await ctx.trigger_typing()

        for m in [await ctx.fetch_message(m) for m in args]:
            commit(StaleView(msg_id=int(m.id)))
            await m.edit(content=None, embeds=m.embeds, view=ArchivedClashView())

        await ctx.reply(f"Successfully killed {len(args)} components.", mention_author=False)
