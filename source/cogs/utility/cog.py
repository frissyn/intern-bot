import nextcord

from ..cog import Base
from .logs import SUBS

from source import COLOR

from nextcord.ext import commands


class Utility(Base):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="util.source")
    async def sauce(self, ctx):
        await ctx.send("https://github.com/frissyn/intern-bot")

    @commands.command(name="util.console")
    async def console(self, ctx, *, payload):
        print(payload)

        with open("db/logs/console.log", "a+") as fh:
            fh.write(payload + "\n")
        
        await ctx.message.add_reaction(r"✔️")
    
    @commands.command(name="util.logs")
    async def logs(self, ctx, file, task, *, options=""):
        file, action = f"db/logs/{file}.log", SUBS[task]
        args, kwargs, opts = [], {}, options.split(" ")

        for item in opts:
            if ":" in item:
                k = item.split(":")
                kwargs.update({k[0]: k[1]})
            else:
                args.append(item)
        
        data = action["exec"](file, *args, **kwargs)

        em = nextcord.Embed(title=f"Logs: {file}", color=COLOR)
        em.description = f"Executed `_{action['def']}`:\n\n"
        em.description += data

        await ctx.reply(embed=em, mention_author=False)