import json
import nextcord

from os import path

from source import COLOR
from source.cogs.cog import Base

from nextcord.ext import commands


class Help(Base):
    def parse_opts(self, opts: str):
        l = [None, None]

        for i, val in enumerate(opts.split(".")):
            if i == 0:
                l[i] = val.title()

            l[i] = val
        
        return l[:2]
    
    def read_help_config(self, cog):
        d = path.dirname(path.abspath(__file__))
        name = cog.__cog_name__.lower()

        with open(f"{d}/../{name}/config/help.json", "r+") as f:
            conf = json.loads(f.read())
        
        return conf
    
    def flat_role_check(self, roles, checks):
        roles = [r.id for r in roles]

        if len(checks) == 0:
            return True

        for r in roles:
            if r in checks: 
                return True
        
        return False
    
    def help_from_cog(self, user, l: list):
        cog = self.bot.cogs.get(l[0].title(), None)

        if cog is None:
            return {"content": f"No such category or cog, **{l[0]}**."}
        
        conf = self.read_help_config(cog)
        em = nextcord.Embed(color=COLOR)

        if l[1] is not None:
            meta = conf["commands"][l[1]]

            if not self.flat_role_check(user.roles, meta['hidden']):
                return {}

            cmd = [c for c in cog.get_commands() if c.qualified_name == '.'.join(l)][0]
        
            em.title = f"Help: {cmd.qualified_name}"
            em.description = f"*{meta['brief']}*\n\n**Usage:** `{meta['usage']}`"
            
            if len(meta['args']) >= 1: em.description += "\n"

            for arg, brief in meta['args'].items():
                em.description += f"*{arg}*: {brief}\n"

            if len(cmd.aliases) >= 1:
                a = [f"`{n}`" for n in cmd.aliases]
                em.description += f"\n**Aliases:** {' '.join(a)}"
            
            return {"embed": em}
        
        em.title = f"Help: {cog.qualified_name}"
        em.description = f"**Type**: {conf['type']}\n"
        em.description += f"**Description**: *{conf['descrip']}*"

        if len(conf['commands']) > 0: em.description += "\n\n"

        for name, meta in conf['commands'].items():
            if not self.flat_role_check(user.roles, meta['hidden']):
                continue
            
            em.description += f"**{l[0]}.{name}** - *{meta['brief']}*\n"
        
        em.set_footer(text="Use `%help {command}` for more detailed help.")
        
        return {"embed": em}

    @commands.command("help")
    async def help_help(self, ctx, opts=None):
        if opts is not None:
            opts = self.parse_opts(opts)
            payload = self.help_from_cog(ctx.author, opts)

            await ctx.send(**payload)

            return