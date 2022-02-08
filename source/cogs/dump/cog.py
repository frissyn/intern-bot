import io
import random
import timeago
import nextcord
import itertools

from ..cog import Base

from source import COLOR

from nextcord.ext import commands

from db import session
from db.models import Tag
from db.models import DumpEntry
from db.models import Attachment


class Dump(Base):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target = 928313138741399603
        self._ago = lambda x: timeago.format(x)

    def _chunks(self, iterable, n, fill=None):
        args = [iter(iterable)] * n

        return itertools.zip_longest(*args, fillvalue=fill)

    def _embed_entry(self, entry: DumpEntry):
        em = nextcord.Embed(color=COLOR)

        em.description = f"Name: {entry.name}\n"
        em.description += f"Tags: {', '.join([str(t) for t in entry.tags])}"
        em.set_image(url=entry.atch.url)

        em.set_footer(
            icon_url=self.bot.user.avatar.url,
            text=f"Tossed into Dumpster {self._ago(entry.stamp)}",
        )

        return em

    def _find(self, name: str):
        entries = session.query(DumpEntry).all()

        for en in entries:
            if name == en.name:
                en

        for en in entries:
            if name in en.name:
                return en

        return None

    async def _files(self, msg, limit=1):
        files = []

        for atch in msg.attachments[:limit]:
            files.append(
                nextcord.File(
                    io.BytesIO(await atch.read()), spoiler=False, filename=atch.filename
                )
            )

        return files

    async def _new_entry(self, name, atch, tags):
        en = DumpEntry(name=name)
        tags = [Tag(name=t) for t in tags]
        atch = Attachment(name=atch.filename, url=atch.url)

        session.add(en)
        session.commit()

        for tag in tags:
            tag.entry_id = en.id

            session.add(tag)

        atch.entry_id = en.id

        session.add(atch)
        session.commit()

        return en

    @commands.command(name="dump.count", aliases=["dump.c", "dc"])
    async def count(self, ctx):
        c = session.query(DumpEntry).count()

        await ctx.send(f"There are currently {c} entries in the Dumpster.")

    @commands.command(name="dump.add", aliases=["dump.a", "da"])
    async def add(self, ctx, name, *, tags=""):
        target = self.bot.get_channel(self.target)
        a = (
            await target.send(
                files=await self._files(ctx.message, 1),
                content=ctx.message.content.strip("%dump.add"),
            )
        ).attachments[0]

        entry = await self._new_entry(name, a, tags.split(" "))

        await ctx.send(embed=self._embed_entry(entry))
        await ctx.message.delete()

    @commands.command(name="quiet-add", aliases=["dump.qa", "dqa"])
    async def qadd(self, ctx, name, *, tags=""):
        target = self.bot.get_channel(self.target)
        a = (
            await target.send(
                files=await self._files(ctx.message, 1),
                content=ctx.message.content.replace("%dump.add", ""),
            )
        ).attachments[0]

        await self._new_entry(name, a, tags.split(" "))
        await ctx.message.add_reaction("🟢")

    @commands.command(name="dump.dive", aliases=["dump.d", "dd"])
    async def search(self, ctx, name):
        en = self._find(name)

        if en:
            await ctx.send(embed=self._embed_entry(en))

    @commands.command(name="dump.sdive", aliases=["dump.sd", "dsd"])
    async def slient_search(self, ctx, name):
        en = self._find(name)

        if en:
            await ctx.send(en.atch.url)

    @commands.command(name="dump.random", aliases=["dump.r", "dr"])
    async def random_(self, ctx, seed=None):
        random.seed(None, 2)

        entries = session.query(DumpEntry).all()
        entry = random.choice(entries)

        await ctx.send(embed=self._embed_entry(entry))

    @commands.command(name="dump.tag", aliases=["dump.t", "dt"])
    async def tag(self, ctx, tag: str):
        tags = session.query(Tag).filter(Tag.name == tag).all()
        entries = [session.query(DumpEntry).get(t.entry_id) for t in tags]

        em = nextcord.Embed(title=f"Dumpster Diving", color=COLOR)
        em.description = f"Found {len(entries)} entries for '{tag}'"

        titles = [f"{i + 1}. {e.name}" for i, e in enumerate(entries)]

        if len(entries) > 0:
            em.description += "\n\n"
            em.description += "\n".join(titles)

        await ctx.send(embed=em)
