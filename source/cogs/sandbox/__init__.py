from .cog import Sandbox


def setup(bot):
    bot.add_cog(Sandbox(bot))