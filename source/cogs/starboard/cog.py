import nextcord

from ..cog import Base

from source import COLOR

from nextcord.ext import commands


class Starboard(Base):
    def __init__(self, bot):
        self.bot = bot
        self.conv = commands.TextChannelConverter()

    @commands.command(name="star.pins")
    async def star_pins(self, ctx, ch, target):
        ch = await self.conv.convert(ctx, ch)
        target = await self.conv.convert(ctx, target)

        for pin in await ch.pins():
            em = nextcord.Embed(title=f"Pinned in {ch.mention}", color=COLOR)
            em.description = pin.content

            if pin.author.avatar:
                em.set_footer(
                    icon_url=pin.author.avatar.url,
                    text=f"{pin.author.name}#{pin.author.discriminator}"
                )
            else:
                em.set_footer(
                    text=f"{pin.author.name}#{pin.author.discriminator}"
                )


            await target.send(embed=em)