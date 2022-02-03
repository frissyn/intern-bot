import json

from nextcord.ext import commands


def _iter(i):
    return i if i else []

def _flat_check(iter, perms):
    flat = [i.id for i in iter]

    for item in flat:
        if flat in perms:
            return True

    return False

def _load_perms_map(name: str):
    path = f"source/cogs/{name.lower()}/config/perms.json"

    with open(path, "r+") as fh:
        return json.loads(fh.read())


class Base(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx):
        user, command = ctx.author, ctx.command
        spec = _load_perms_map(self.qualified_name)

        perms = spec.get(command.name)
        perms = perms if perms else spec["*"]

        if perms == "*":
            return True
        
        if user.id in _iter(perms.get("members")):
            return True
        
        for role in _iter(perms.get("min_roles")):
            if user.top_role >= ctx.guild.get_role(role):
                return True 
        
        if ctx.channel.id in _iter(perms.get("channels")):
            return True

        return await ctx.message.add_reaction(r"❌") and False
