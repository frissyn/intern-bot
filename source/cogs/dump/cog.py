import io
import timeago
import nextcord

from ..cog import Base

from source import COLOR

from nextcord.ext import commands

from db.handle import session

from db.handle import Tag
from db.handle import DumpEntry
from db.handle import Attachment


class Dump(Base):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target = 928313138741399603
    
    def _ago(self, stamp):
        return timeago.format(stamp)

    def _embed_entry(self, entry: DumpEntry):
        em = nextcord.Embed(color=COLOR)

        em.description = f"Name: {entry.name}\n"
        em.description += f"Tags: {', '.join([str(t) for t in entry.tags])}"
        em.set_image(url=entry.atch.url)

        em.set_footer(
            icon_url=self.bot.user.avatar.url,
            text=f"Tossed into Dumpster {self._ago(entry.stamp)}"
        )

        return em

    async def _files(self, msg, limit=1):
        files = []

        for atch in msg.attachments[:limit]:
            files.append(
                nextcord.File(
                    io.BytesIO(await atch.read()),
                    spoiler=False, filename=atch.filename
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
    
    @commands.command(name="dump.add")
    async def add(self, ctx, name, *, tags=""):
        target = self.bot.get_channel(self.target)
        a = (await target.send(
            files=await self._files(ctx.message, 1),
            content=ctx.message.content.strip("%dump.add")
        )).attachments[0]

        
        entry = await self._new_entry(name, a, tags.split(" "))

        await ctx.send(embed=self._embed_entry(entry))
        await ctx.message.delete()

    @commands.command(name="dump.dive")
    async def search(self, ctx, name):
        entries = session.qeury