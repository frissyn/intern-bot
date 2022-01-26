import json

from nextcord.ext import commands


def _iter(i):
    return i if i else []


def flat_check(iter, perms):
    flat = [i.id  for i in iter]

    for item in flat:
        if flat in perms:
            return True
    
    return False


def load_perms_map(name: str):
    path = f"source/cogs/{name.lower()}/perms.json"

    with open(path, "r+") as fh:
        return json.loads(fh.read())


class Base(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx):
        user, command = ctx.author, ctx.command
        perms = load_perms_map(self.qualified_name)

        spec = perms.get(command.name)
        spec = spec if spec else perms["*"]
        
        if spec == "*": return True

        if user.id in _iter(spec.get("members")):
            return True
        
        if flat_check(ctx.author.roles[1:], _iter(spec.get("roles"))):
            return True
        
        if flat_check(ctx.guild.channels, _iter(perms.get("channels"))):
            return True

        return (await ctx.message.add_reaction(r"❌") and False)
