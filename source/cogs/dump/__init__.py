from .cog import Dump


def setup(bot):
    bot.add_cog(Dump(bot))